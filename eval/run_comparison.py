"""
Unified Comparative Benchmark Runner: Native-Audio LLM vs. Cascaded STT->LLM->TTS
Evaluates document-grounded spoken QA across factual accuracy, adversarial abstention, latency, and cost.

Outputs:
- eval/results_comparison_<timestamp>.json
- eval/results_comparison_latest.json
- eval/checkpoint_comparison.json (incremental checkpointing for resume)
"""

import os
import sys
import time
import json
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv
load_dotenv(REPO_ROOT / ".env")

import main
import google.generativeai as genai

from eval.native_arm import run_native_arm, call_with_retry, ArmResult
from eval.cascade_arm import run_cascade_arm, get_whisper_model

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_comparison")

EVAL_DIR = REPO_ROOT / "eval"
DATA_DIR = EVAL_DIR / "data"
AUDIO_DIR = EVAL_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Standard pricing for Gemini Flash (per 1,000,000 tokens)
# Free Tier actual charged cost is $0.00; these rates compute theoretical list-price cost:
PRICING_PER_1M_TOKENS = {
    "text_input": 0.10,     # $0.10 / 1M text tokens
    "audio_input": 0.70,    # $0.70 / 1M audio tokens
    "text_output": 0.40     # $0.40 / 1M output text tokens
}


def compute_cost_usd(arm: str, prompt_tokens: int, candidates_tokens: int) -> float:
    """Computes estimated Gemini API cost in USD based on official token pricing."""
    if arm == "native":
        # In multimodal native arm, input includes audio data
        input_rate = PRICING_PER_1M_TOKENS["audio_input"]
    else:
        # In cascade arm, input to LLM is text-only
        input_rate = PRICING_PER_1M_TOKENS["text_input"]
    output_rate = PRICING_PER_1M_TOKENS["text_output"]

    cost = (prompt_tokens * (input_rate / 1_000_000)) + (candidates_tokens * (output_rate / 1_000_000))
    return round(cost, 7)


def calc_latency_stats(times: List[float]) -> Dict[str, float]:
    """Computes mean, p95, min, and max latency stats."""
    if not times:
        return {"mean": 0.0, "p95": 0.0, "min": 0.0, "max": 0.0}
    times_sorted = sorted(times)
    mean_val = sum(times_sorted) / len(times_sorted)
    idx_95 = int(0.95 * len(times_sorted))
    p95_val = times_sorted[min(idx_95, len(times_sorted) - 1)]
    return {
        "mean": round(mean_val, 3),
        "p95": round(p95_val, 3),
        "min": round(times_sorted[0], 3),
        "max": round(times_sorted[-1], 3)
    }


def synthesize_missing_wavs(questions: List[Dict[str, str]]) -> int:
    """Synthesizes any missing question audio files offline using Windows System.Speech."""
    import subprocess
    synthesized = 0
    for q in questions:
        qid = q["question_id"]
        qtext = q.get("question_text") or q.get("question", "")
        wav_path = AUDIO_DIR / f"{qid}.wav"
        if not (wav_path.exists() and wav_path.stat().st_size > 1000):
            logger.info(f"Synthesizing offline audio for [{qid}]...")
            safe_text = qtext.replace("'", "''")
            ps_cmd = f"""
Add-Type -AssemblyName System.Speech
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
$s.SetOutputToWaveFile('{str(wav_path.resolve())}')
$s.Speak('{safe_text}')
$s.Dispose()
"""
            res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
            if res.returncode != 0:
                raise RuntimeError(f"PowerShell audio synthesis failed for {qid}: {res.stderr}")
            synthesized += 1
    return synthesized


def judge_batch(items: List[Dict[str, Any]], judge_model, chunk_size: int = 10) -> Dict[str, Dict[str, Any]]:
    """
    Evaluates answers using the LLM-as-judge rubric from eval/RUBRIC.md.
    Evaluates both native and cascade answers for given items in chunks to avoid output token limits.
    Returns mapping: f"{qid}___{arm}" -> {"score": int, "evidence_span": str, "justification": str}
    """
    all_judgments: Dict[str, Dict[str, Any]] = {}

    for chunk_start in range(0, len(items), chunk_size):
        chunk_items = items[chunk_start:chunk_start + chunk_size]
        prompt = """You are an impartial, rigorous evaluation judge auditing an AI spoken document Q&A assistant according to eval/RUBRIC.md.

Scoring Rules:
For factual questions:
- 2 = Full Credit (Correct): Factually exact and complete. Directly states the ground-truth fact, metric, threshold, or definition.
- 1 = Partial Credit (Substantially Correct): Correct core substance, but missing a secondary qualifier or has minor rounding that does not alter factual correctness.
- 0 = No Credit (Incorrect): Factually wrong, contradictory, or claims missing when present.

For adversarial questions (unanswerable from document):
- 2 = Full Credit (Resisted): Explicitly states the document does not mention or contain this information (correct abstention).
- 1 = Partial Credit (Hedged): Notes document lacks it, but speculates or answers from external knowledge.
- 0 = No Credit (Hallucinated): Invents an answer claiming it was in the document.

Auditable Evidence Standard:
You MUST provide an exact evidence quote span from the model answer justifying every rating.

Here are the Q&A pairs to evaluate:
"""

        eval_targets = []
        for item in chunk_items:
            qid = item["question_id"]
            qtype = item["question_type"]
            question = item.get("question_text") or item.get("question", "")
            expected = item.get("ground_truth") or item.get("expected_answer", "")

            # Native answer
            eval_targets.append({
                "target_id": f"{qid}___native",
                "qid": qid,
                "arm": "native",
                "type": qtype,
                "question": question,
                "expected": expected,
                "answer": item["native"]["answer"]
            })

            # Cascade answer
            eval_targets.append({
                "target_id": f"{qid}___cascade",
                "qid": qid,
                "arm": "cascade",
                "type": qtype,
                "question": question,
                "expected": expected,
                "answer": item["cascade"]["answer"]
            })

        for idx, t in enumerate(eval_targets, 1):
            prompt += f"""
--- Target {idx} ---
Target ID: {t['target_id']}
Question ID: {t['qid']} | Arm: {t['arm']}
Question Type: {t['type']}
Question: {t['question']}
Expected Ground Truth: {t['expected']}
Model Answer:
\"\"\"{t['answer']}\"\"\"
"""

        prompt += """
Respond ONLY with a valid JSON array of objects in this exact structure:
[
  {
    "target_id": "Q-DLH-01___native",
    "score": 2,
    "evidence_span": "<exact quote from model answer>",
    "justification": "<one sentence justification>"
  },
  ...
]
"""

        judge_resp = call_with_retry(judge_model.generate_content, prompt, request_options={"timeout": 90.0})
        raw_judge = judge_resp.text.strip()
        if raw_judge.startswith("```json"):
            raw_judge = raw_judge[7:]
        if raw_judge.startswith("```"):
            raw_judge = raw_judge[3:]
        if raw_judge.endswith("```"):
            raw_judge = raw_judge[:-3]
        raw_judge = raw_judge.strip()

        try:
            judgments = json.loads(raw_judge)
            for j in judgments:
                all_judgments[j["target_id"]] = j
        except Exception as e:
            logger.error(f"Failed to parse batch judge response: {e}\nRaw: {raw_judge[:300]}")
            # Fallback to individual scoring or safe default
            for t in eval_targets:
                all_judgments[t["target_id"]] = {
                    "score": 0,
                    "evidence_span": "Parse error",
                    "justification": f"Judge response was invalid JSON: {str(e)}"
                }

    return all_judgments


def run_comparison(
    dataset_path: Optional[Path] = None,
    limit: Optional[int] = None,
    whisper_size: str = "base",
    delay_between_calls: float = 4.0,
    checkpoint_file: Path = EVAL_DIR / "checkpoint_comparison.json",
    no_cache: bool = False
) -> Dict[str, Any]:
    """
    Main comparative execution loop running Native and Cascade arms over the dataset.
    """
    if dataset_path is None:
        v2_path = EVAL_DIR / "dataset_v2.csv"
        dataset_path = v2_path if v2_path.exists() else (EVAL_DIR / "dataset.csv")

    with open(dataset_path, "r", encoding="utf-8") as f:
        all_questions = list(csv.DictReader(f))

    total_dataset_questions = len(all_questions)
    questions = all_questions
    if limit is not None and limit > 0:
        questions = all_questions[:limit]

    logger.info(f"Loaded {len(questions)} evaluation questions from {dataset_path.name}")

    # Ensure offline audio files exist
    newly_synth = synthesize_missing_wavs(questions)
    if newly_synth > 0:
        logger.info(f"Synthesized {newly_synth} missing WAV files offline.")

    # Preload Whisper model on CPU
    logger.info(f"Preloading faster-whisper model '{whisper_size}' on CPU...")
    get_whisper_model(model_size=whisper_size, device="cpu", compute_type="int8")

    # Load checkpoint if available and not no_cache
    checkpoint_data = {}
    if not no_cache and checkpoint_file.exists():
        try:
            with open(checkpoint_file, "r", encoding="utf-8") as f:
                checkpoint_data = json.load(f)
                logger.info(f"Loaded checkpoint with {len(checkpoint_data.get('items', []))} completed questions.")
        except Exception as e:
            logger.warning(f"Could not read checkpoint file: {e}")

    cached_items_map = {item["question_id"]: item for item in checkpoint_data.get("items", [])}

    processed_items: List[Dict[str, Any]] = []
    api_calls_count = 0

    for idx, q in enumerate(questions, 1):
        qid = q["question_id"]
        pdf_name = q.get("pdf_id") or q.get("pdf")
        qtype = q["question_type"]
        qtext = q.get("question_text") or q.get("question")
        expected = q.get("ground_truth") or q.get("expected_answer")
        page_hint = q.get("evidence_span") or q.get("page_hint")
        wav_path = AUDIO_DIR / f"{qid}.wav"

        logger.info(f"\n=======================================================")
        logger.info(f"Processing Item {idx}/{len(questions)}: [{qid}] ({qtype}) for {pdf_name}")
        logger.info(f"Question: {qtext}")
        logger.info(f"=======================================================")

        # Check if already processed in checkpoint
        if qid in cached_items_map and "native" in cached_items_map[qid] and "cascade" in cached_items_map[qid]:
            logger.info(f"Using checkpointed result for [{qid}].")
            processed_items.append(cached_items_map[qid])
            continue

        item_result = {
            "question_id": qid,
            "pdf": pdf_name,
            "question_type": qtype,
            "question": qtext,
            "expected_answer": expected,
            "page_hint": page_hint,
            "wav_path": str(wav_path)
        }

        # 1. Native Arm
        logger.info(f"-> Executing Native Arm on [{qid}]...")
        t0 = time.perf_counter()
        try:
            native_res = run_native_arm(pdf_name, qid, wav_path)
            api_calls_count += 1
            native_cost = compute_cost_usd(
                "native",
                native_res.tokens_used.get("prompt_tokens", 0),
                native_res.tokens_used.get("candidates_tokens", 0)
            )
            item_result["native"] = {
                "answer": native_res.answer,
                "stage_latencies": native_res.stage_latencies,
                "tokens_used": native_res.tokens_used,
                "estimated_cost_usd": native_cost,
                "raw_response": native_res.raw_response,
                "sentiment": native_res.sentiment,
                "error": None
            }
            logger.info(f"   Native Arm: answer='{native_res.answer[:60]}...' latency={native_res.stage_latencies['total']}s")
        except Exception as e:
            logger.error(f"   Native Arm FAILED on [{qid}]: {e}", exc_info=True)
            item_result["native"] = {
                "answer": f"ERROR: {str(e)}",
                "stage_latencies": {"stt": 0.0, "llm": 0.0, "tts": 0.0, "total": 0.0},
                "tokens_used": {"prompt_tokens": 0, "candidates_tokens": 0, "total_tokens": 0},
                "estimated_cost_usd": 0.0,
                "error": str(e)
            }

        # Rate-limit spacing
        time.sleep(delay_between_calls)

        # 2. Cascade Arm
        logger.info(f"-> Executing Cascade Arm on [{qid}]...")
        try:
            cascade_res = run_cascade_arm(pdf_name, qid, wav_path, whisper_model_size=whisper_size)
            api_calls_count += 1
            cascade_cost = compute_cost_usd(
                "cascade",
                cascade_res.tokens_used.get("prompt_tokens", 0),
                cascade_res.tokens_used.get("candidates_tokens", 0)
            )
            item_result["cascade"] = {
                "transcript": cascade_res.transcript,
                "answer": cascade_res.answer,
                "stage_latencies": cascade_res.stage_latencies,
                "tokens_used": cascade_res.tokens_used,
                "estimated_cost_usd": cascade_cost,
                "raw_response": cascade_res.raw_response,
                "error": None
            }
            logger.info(
                f"   Cascade Arm: transcript='{cascade_res.transcript}' "
                f"latency_stt={cascade_res.stage_latencies['stt']}s "
                f"latency_llm={cascade_res.stage_latencies['llm']}s "
                f"total={cascade_res.stage_latencies['total']}s"
            )
        except Exception as e:
            logger.error(f"   Cascade Arm FAILED on [{qid}]: {e}", exc_info=True)
            item_result["cascade"] = {
                "transcript": "",
                "answer": f"ERROR: {str(e)}",
                "stage_latencies": {"stt": 0.0, "llm": 0.0, "tts": 0.0, "total": 0.0},
                "tokens_used": {"prompt_tokens": 0, "candidates_tokens": 0, "total_tokens": 0},
                "estimated_cost_usd": 0.0,
                "error": str(e)
            }

        processed_items.append(item_result)

        # Incremental checkpoint update
        with open(checkpoint_file, "w", encoding="utf-8") as f:
            json.dump({"items": processed_items, "last_updated": datetime.now().isoformat()}, f, indent=2)

        # Rate-limit spacing
        time.sleep(delay_between_calls)

    # 3. LLM-as-Judge Scoring per Document
    logger.info("\n=======================================================")
    logger.info("Executing Batch LLM-as-Judge Evaluation across both arms...")
    logger.info("=======================================================")

    judge_model = genai.GenerativeModel(main.GEMINI_MODEL)
    pdfs = sorted(list(set(it["pdf"] for it in processed_items)))

    for pdf_name in pdfs:
        doc_items = [it for it in processed_items if it["pdf"] == pdf_name]
        # Check if already judged
        unjudged = [it for it in doc_items if "score" not in it.get("native", {}) or "score" not in it.get("cascade", {})]
        if not unjudged:
            logger.info(f"Document {pdf_name} already scored in checkpoint.")
            continue

        logger.info(f"Judging {len(doc_items)} questions for {pdf_name}...")
        judge_map = judge_batch(doc_items, judge_model)
        api_calls_count += 1

        for it in doc_items:
            qid = it["question_id"]
            qtype = it["question_type"]

            # Score native
            nat_eval = judge_map.get(f"{qid}___native", {"score": 0, "evidence_span": "N/A", "justification": "Not judged"})
            it["native"]["score"] = nat_eval["score"]
            it["native"]["evidence_span"] = nat_eval.get("evidence_span", "")
            it["native"]["justification"] = nat_eval.get("justification", "")
            if qtype == "adversarial":
                it["native"]["abstention_correct"] = (nat_eval["score"] == 2)
            else:
                it["native"]["abstention_correct"] = None

            # Score cascade
            casc_eval = judge_map.get(f"{qid}___cascade", {"score": 0, "evidence_span": "N/A", "justification": "Not judged"})
            it["cascade"]["score"] = casc_eval["score"]
            it["cascade"]["evidence_span"] = casc_eval.get("evidence_span", "")
            it["cascade"]["justification"] = casc_eval.get("justification", "")
            if qtype == "adversarial":
                it["cascade"]["abstention_correct"] = (casc_eval["score"] == 2)
            else:
                it["cascade"]["abstention_correct"] = None

            # Agreement flag
            it["arms_agree"] = (it["native"]["score"] == it["cascade"]["score"])
            if it["native"]["score"] == it["cascade"]["score"]:
                it["disagreement_type"] = "none"
            elif qtype == "adversarial" and (it["native"]["abstention_correct"] != it["cascade"]["abstention_correct"]):
                it["disagreement_type"] = "abstention_mismatch"
            else:
                it["disagreement_type"] = "accuracy_mismatch"

        # Update checkpoint with scores
        with open(checkpoint_file, "w", encoding="utf-8") as f:
            json.dump({"items": processed_items, "last_updated": datetime.now().isoformat()}, f, indent=2)

        time.sleep(delay_between_calls)

    # 4. Aggregate Metrics
    factual_items = [it for it in processed_items if it["question_type"] == "factual"]
    adversarial_items = [it for it in processed_items if it["question_type"] == "adversarial"]

    def compute_arm_summary(arm_name: str) -> Dict[str, Any]:
        fact_pts = sum(it[arm_name]["score"] for it in factual_items)
        fact_max = len(factual_items) * 2
        fact_acc = round((fact_pts / fact_max) * 100, 1) if fact_max > 0 else 0.0

        adv_pts = sum(it[arm_name]["score"] for it in adversarial_items)
        adv_max = len(adversarial_items) * 2
        halluc_res = round((adv_pts / adv_max) * 100, 1) if adv_max > 0 else 0.0

        abstentions = sum(1 for it in adversarial_items if it[arm_name]["score"] == 2)
        abstention_rate = round((abstentions / len(adversarial_items)) * 100, 1) if adversarial_items else 0.0

        total_pts = sum(it[arm_name]["score"] for it in processed_items)
        total_max = len(processed_items) * 2
        overall_pct = round((total_pts / total_max) * 100, 1) if total_max > 0 else 0.0

        score_counts = {
            "score_2": sum(1 for it in processed_items if it[arm_name]["score"] == 2),
            "score_1": sum(1 for it in processed_items if it[arm_name]["score"] == 1),
            "score_0": sum(1 for it in processed_items if it[arm_name]["score"] == 0)
        }

        stt_times = [it[arm_name]["stage_latencies"]["stt"] for it in processed_items if it[arm_name]["stage_latencies"]["stt"] > 0]
        llm_times = [it[arm_name]["stage_latencies"]["llm"] for it in processed_items if it[arm_name]["stage_latencies"]["llm"] > 0]
        total_times = [it[arm_name]["stage_latencies"]["total"] for it in processed_items if it[arm_name]["stage_latencies"]["total"] > 0]

        total_prompt_tok = sum(it[arm_name]["tokens_used"].get("prompt_tokens", 0) for it in processed_items)
        total_cand_tok = sum(it[arm_name]["tokens_used"].get("candidates_tokens", 0) for it in processed_items)
        total_tok = sum(it[arm_name]["tokens_used"].get("total_tokens", 0) for it in processed_items)
        total_cost = round(sum(it[arm_name]["estimated_cost_usd"] for it in processed_items), 5)

        return {
            "factual_accuracy_pct": fact_acc,
            "factual_points": fact_pts,
            "factual_max": fact_max,
            "hallucination_resistance_pct": halluc_res,
            "adversarial_points": adv_pts,
            "adversarial_max": adv_max,
            "abstention_rate_pct": abstention_rate,
            "abstention_count": abstentions,
            "abstention_max": len(adversarial_items),
            "overall_benchmark_pct": overall_pct,
            "total_points": total_pts,
            "total_max": total_max,
            "score_counts": score_counts,
            "latencies": {
                "stt": calc_latency_stats(stt_times),
                "llm": calc_latency_stats(llm_times),
                "tts": {"mean": 0.0, "p95": 0.0, "status": "SKIPPED"},
                "total": calc_latency_stats(total_times)
            },
            "tokens": {
                "prompt_tokens": total_prompt_tok,
                "candidates_tokens": total_cand_tok,
                "total_tokens": total_tok
            },
            "estimated_api_cost_usd": total_cost,
            "actual_charged_cost_usd": 0.00
        }

    native_summary = compute_arm_summary("native")
    cascade_summary = compute_arm_summary("cascade")

    deltas = {
        "accuracy_delta_pct": round(cascade_summary["factual_accuracy_pct"] - native_summary["factual_accuracy_pct"], 1),
        "hallucination_resistance_delta_pct": round(cascade_summary["hallucination_resistance_pct"] - native_summary["hallucination_resistance_pct"], 1),
        "abstention_rate_delta_pct": round(cascade_summary["abstention_rate_pct"] - native_summary["abstention_rate_pct"], 1),
        "overall_benchmark_delta_pct": round(cascade_summary["overall_benchmark_pct"] - native_summary["overall_benchmark_pct"], 1),
        "mean_latency_delta_sec": round(cascade_summary["latencies"]["total"]["mean"] - native_summary["latencies"]["total"]["mean"], 3),
        "cost_delta_usd": round(cascade_summary["estimated_api_cost_usd"] - native_summary["estimated_api_cost_usd"], 5)
    }

    # Per-PDF breakdown
    per_pdf_stats = {}
    for p in pdfs:
        p_items = [it for it in processed_items if it["pdf"] == p]
        p_fact = [it for it in p_items if it["question_type"] == "factual"]
        p_adv = [it for it in p_items if it["question_type"] == "adversarial"]

        def pdf_arm_stat(arm_name):
            f_pts = sum(it[arm_name]["score"] for it in p_fact)
            f_max = len(p_fact) * 2
            a_pts = sum(it[arm_name]["score"] for it in p_adv)
            a_max = len(p_adv) * 2
            return {
                "factual_acc_pct": round((f_pts / f_max) * 100, 1) if f_max else 0.0,
                "halluc_res_pct": round((a_pts / a_max) * 100, 1) if a_max else 0.0,
                "total_pts": f_pts + a_pts,
                "total_max": f_max + a_max,
                "overall_pct": round(((f_pts + a_pts) / (f_max + a_max)) * 100, 1) if (f_max + a_max) else 0.0
            }

        per_pdf_stats[p] = {
            "total_questions": len(p_items),
            "native": pdf_arm_stat("native"),
            "cascade": pdf_arm_stat("cascade")
        }

    # Save final results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if len(processed_items) >= 200 or "v2" in dataset_path.name:
        out_file = EVAL_DIR / f"results_comparison_n200_{timestamp}.json"
    else:
        out_file = EVAL_DIR / f"results_comparison_{timestamp}.json"
    latest_file = EVAL_DIR / "results_comparison_latest.json"

    comparison_payload = {
        "timestamp": timestamp,
        "model_used": main.GEMINI_MODEL,
        "whisper_model": whisper_size,
        "whisper_device": "cpu",
        "dataset_file": str(dataset_path.name),
        "total_questions": len(processed_items),
        "factual_questions": len(factual_items),
        "adversarial_questions": len(adversarial_items),
        "summary_metrics": {
            "native": native_summary,
            "cascade": cascade_summary,
            "deltas": deltas
        },
        "per_pdf_stats": per_pdf_stats,
        "total_api_calls_made": api_calls_count,
        "itemized_results": processed_items
    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(comparison_payload, f, indent=2)

    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(comparison_payload, f, indent=2)

    # Clean up checkpoint only upon complete success of full dataset
    if checkpoint_file.exists() and (limit is None or len(processed_items) >= total_dataset_questions):
        try:
            checkpoint_file.unlink()
        except Exception:
            pass

    # Print summary table
    print("\n" + "=" * 75)
    print("COMPARATIVE EVALUATION BENCHMARK: NATIVE-AUDIO vs. CASCADED PIPELINE")
    print("=" * 75)
    print(f"Model Evaluated:                 {main.GEMINI_MODEL}")
    print(f"Local STT Engine:                faster-whisper ({whisper_size}, CPU int8)")
    print(f"Total Questions Evaluated:       {len(processed_items)} ({len(factual_items)} factual, {len(adversarial_items)} adversarial)")
    print("-" * 75)
    print(f"{'METRIC':<30} | {'NATIVE ARM':<16} | {'CASCADE ARM':<16} | {'DELTA (Casc - Nat)':<15}")
    print("-" * 75)
    print(f"{'Factual Accuracy Rate':<30} | {native_summary['factual_accuracy_pct']:>14.1f}% | {cascade_summary['factual_accuracy_pct']:>14.1f}% | {deltas['accuracy_delta_pct']:>+13.1f}%")
    print(f"{'Hallucination Resistance':<30} | {native_summary['hallucination_resistance_pct']:>14.1f}% | {cascade_summary['hallucination_resistance_pct']:>14.1f}% | {deltas['hallucination_resistance_delta_pct']:>+13.1f}%")
    print(f"{'Abstention Rate (Adversarial)':<30} | {native_summary['abstention_rate_pct']:>14.1f}% | {cascade_summary['abstention_rate_pct']:>14.1f}% | {deltas['abstention_rate_delta_pct']:>+13.1f}%")
    print(f"{'Combined Benchmark Accuracy':<30} | {native_summary['overall_benchmark_pct']:>14.1f}% | {cascade_summary['overall_benchmark_pct']:>14.1f}% | {deltas['overall_benchmark_delta_pct']:>+13.1f}%")
    print("-" * 75)
    print(f"{'Mean Total Latency':<30} | {native_summary['latencies']['total']['mean']:>14.3f}s | {cascade_summary['latencies']['total']['mean']:>14.3f}s | {deltas['mean_latency_delta_sec']:>+13.3f}s")
    print(f"{'  - STT Latency (Whisper)':<30} | {'0.000s':>15} | {cascade_summary['latencies']['stt']['mean']:>14.3f}s |")
    print(f"{'  - LLM Inference Latency':<30} | {native_summary['latencies']['llm']['mean']:>14.3f}s | {cascade_summary['latencies']['llm']['mean']:>14.3f}s |")
    print(f"{'p95 Total Latency':<30} | {native_summary['latencies']['total']['p95']:>14.3f}s | {cascade_summary['latencies']['total']['p95']:>14.3f}s |")
    print("-" * 75)
    print(f"{'Total Tokens Consumed':<30} | {native_summary['tokens']['total_tokens']:>15} | {cascade_summary['tokens']['total_tokens']:>15} |")
    print(f"{'Estimated API Cost (List)':<30} | ${native_summary['estimated_api_cost_usd']:>14.5f} | ${cascade_summary['estimated_api_cost_usd']:>14.5f} | ${deltas['cost_delta_usd']:>+13.5f}")
    print(f"{'Actual Billed Cost (Free Tier)':<30} | {'$0.00':>15} | {'$0.00':>15} | {'$0.00':>15}")
    print("=" * 75)
    print(f"Results saved to: {out_file.name} and {latest_file.name}\n")

    return comparison_payload


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run Head-to-Head Comparative Study: Native vs. Cascade Arm")
    parser.add_argument("--dataset", default=None, help="Dataset CSV path (default: eval/dataset_v2.csv if exists, else dataset.csv)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of questions to evaluate (default: all)")
    parser.add_argument("--whisper-size", default="base", help="faster-whisper model size (default: base)")
    parser.add_argument("--delay", type=float, default=4.0, help="Delay between API calls in seconds (default: 4.0)")
    parser.add_argument("--no-cache", action="store_true", help="Do not load from checkpoint")
    args = parser.parse_args()

    dataset_p = Path(args.dataset) if args.dataset else None
    run_comparison(dataset_path=dataset_p, limit=args.limit, whisper_size=args.whisper_size, delay_between_calls=args.delay, no_cache=args.no_cache)
