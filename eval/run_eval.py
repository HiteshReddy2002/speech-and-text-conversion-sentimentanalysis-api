"""
Evaluation Harness for speech-and-text-conversion-sentimentanalysis-api.
Runs actual repository pipeline functions:
- extract_text_from_pdf
- summarize_book
- process_query_with_llm (multimodal audio WAV query via inline_data)

Features:
- Incremental checkpointing to eval/checkpoint.json after every question
- Document summary caching in eval/doc_summaries.json
- Robust rate-limit backoff with progressive retry delays
- LLM-as-judge scoring with exact evidence span quoting (eval/RUBRIC.md)
"""

import os
import sys
import time
import json
import csv
import logging
from datetime import datetime
from pathlib import Path
import subprocess

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv
load_dotenv(REPO_ROOT / ".env")

import main
import google.generativeai as genai

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

EVAL_DIR = REPO_ROOT / "eval"
DATA_DIR = EVAL_DIR / "data"
AUDIO_DIR = EVAL_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def synthesize_wav_offline(text: str, output_path: Path) -> Path:
    """Synthesizes text to a standard 16-bit PCM WAV using Windows System.Speech offline."""
    if output_path.exists() and output_path.stat().st_size > 1000:
        return output_path
    
    safe_text = text.replace("'", "''")
    ps_cmd = f"""
Add-Type -AssemblyName System.Speech
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
$s.SetOutputToWaveFile('{str(output_path.resolve())}')
$s.Speak('{safe_text}')
$s.Dispose()
"""
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_cmd],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"PowerShell offline audio synthesis failed: {result.stderr}")
    return output_path


def call_with_retry(fn, *args, max_retries=10, delay=10, **kwargs):
    """Executes a Gemini API call with resilient progressive backoff on rate limits."""
    for attempt in range(max_retries):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            logging.warning(f"Exception in call_with_retry: {e}")
            err_str = str(e).lower()
            if "resource_exhausted" in err_str or "429" in err_str or "quota" in err_str:
                wait_time = min(75, delay * (attempt + 1))
                logging.warning(f"Rate limited (attempt {attempt+1}/{max_retries}). Backing off for {wait_time}s...")
                time.sleep(wait_time)
            else:
                logging.error(f"API call failed: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(delay)
    raise RuntimeError("Max retries exceeded.")


def score_with_judge(question: str, expected: str, model_answer: str, q_type: str, judge_model) -> dict:
    """
    LLM-as-judge scoring adhering to eval/RUBRIC.md.
    Returns: {"score": int (0, 1, or 2), "evidence_span": str, "justification": str}
    """
    if q_type == "adversarial":
        prompt = f"""
You are an impartial, rigorous evaluation judge auditing an AI document Q&A assistant for hallucination resistance.

The question asked about information that is NOT present in the reference document.
Question: {question}
Expected behavior: The assistant should decline to answer, state that the document does not contain this information, or indicate lack of data.

Model Answer to evaluate:
\"\"\"{model_answer}\"\"\"

Scoring Rubric:
2 = Full Credit (Resisted): The model explicitly declines or states that the document/summary does not mention or contain this information.
1 = Partial Credit (Hedged): The model expresses doubt or states it cannot verify from the document, but provides speculative general information.
0 = No Credit (Hallucinated): The model invents a concrete answer, fabricating numbers, policies, or facts as if they were present in the document.

Respond ONLY with valid JSON in this exact structure:
{{
  "score": 2,
  "evidence_span": "<exact quote from model answer showing refusal or hallucination>",
  "justification": "<one sentence explaining the score>"
}}
"""
    else:
        prompt = f"""
You are an impartial, rigorous evaluation judge auditing an AI document Q&A assistant for factual accuracy.

Question: {question}
Ground Truth Expected Answer: {expected}

Model Answer to evaluate:
\"\"\"{model_answer}\"\"\"

Scoring Rubric:
2 = Full Credit (Correct): Factually exact and complete. Directly states the ground-truth fact, metric, threshold, or definition.
1 = Partial Credit (Substantially Correct): Correct core substance, but missing a secondary qualifier or has minor rounding that does not alter factual correctness.
0 = No Credit (Incorrect): Factually wrong, contradictory, or claims the answer is missing when it is provided.

Respond ONLY with valid JSON in this exact structure:
{{
  "score": 2,
  "evidence_span": "<exact quote from model answer matching or contradicting ground truth>",
  "justification": "<one sentence explaining the score>"
}}
"""

    resp = call_with_retry(judge_model.generate_content, prompt)
    raw_text = resp.text.strip()
    
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:]
    if raw_text.startswith("```"):
        raw_text = raw_text[3:]
    if raw_text.endswith("```"):
        raw_text = raw_text[:-3]
    raw_text = raw_text.strip()

    try:
        parsed = json.loads(raw_text)
        score = int(parsed.get("score", 0))
        return {
            "score": score if score in (0, 1, 2) else 0,
            "evidence_span": str(parsed.get("evidence_span", "")),
            "justification": str(parsed.get("justification", ""))
        }
    except Exception as e:
        logging.warning(f"Could not parse judge response as JSON: {raw_text}. Error: {e}")
        return {
            "score": 0,
            "evidence_span": "JSON parse error",
            "justification": f"Judge response was not valid JSON: {raw_text[:100]}"
        }


def main_eval():
    dataset_path = EVAL_DIR / "dataset.csv"
    if not dataset_path.exists():
        logging.error(f"Dataset file not found: {dataset_path}")
        sys.exit(1)

    with open(dataset_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        questions = list(reader)

    logging.info(f"Loaded {len(questions)} evaluation questions from {dataset_path.name}")

    judge_model = genai.GenerativeModel(main.GEMINI_MODEL)

    # Load checkpoint if available
    checkpoint_file = EVAL_DIR / "checkpoint.json"
    results = []
    completed_qids = set()
    if checkpoint_file.exists():
        try:
            with open(checkpoint_file, "r", encoding="utf-8") as f:
                saved_data = json.load(f)
                results = saved_data.get("results", [])
                completed_qids = {r["question_id"] for r in results}
                logging.info(f"Loaded {len(results)} previously checkpointed question results.")
        except Exception as e:
            logging.warning(f"Could not load checkpoint: {e}")

    # Load cached summaries if available
    summaries_file = EVAL_DIR / "doc_summaries.json"
    doc_summaries = {}
    if summaries_file.exists():
        try:
            with open(summaries_file, "r", encoding="utf-8") as f:
                doc_summaries = json.load(f)
                logging.info(f"Loaded {len(doc_summaries)} cached document summaries.")
        except Exception as e:
            logging.warning(f"Could not load doc summaries: {e}")

    # Group questions by PDF
    pdfs = sorted(list(set(q["pdf"] for q in questions)))
    
    stage_timings = {
        "pdf_extraction": [],
        "summarization": [],
        "audio_qa_inference": []
    }

    doc_extracted_text = {}

    for pdf_name in pdfs:
        pdf_path = DATA_DIR / pdf_name
        if not pdf_path.exists():
            logging.error(f"PDF not found: {pdf_path}")
            continue

        logging.info(f"=== Processing PDF: {pdf_name} ===")

        # Stage 1: PDF Extraction
        t0 = time.perf_counter()
        extracted_text = main.extract_text_from_pdf(str(pdf_path))
        t_extract = time.perf_counter() - t0
        stage_timings["pdf_extraction"].append(t_extract)
        doc_extracted_text[pdf_name] = extracted_text

        # Stage 2: Document Summarization
        if pdf_name in doc_summaries:
            summary = doc_summaries[pdf_name]
            t_summary = 0.0
            logging.info(f"Using cached summary for {pdf_name} ({len(summary)} chars)")
        else:
            t0 = time.perf_counter()
            summary = call_with_retry(main.summarize_book, extracted_text)
            t_summary = time.perf_counter() - t0
            stage_timings["summarization"].append(t_summary)
            doc_summaries[pdf_name] = summary
            with open(summaries_file, "w", encoding="utf-8") as f:
                json.dump(doc_summaries, f, indent=2)
            logging.info(f"Generated summary ({len(summary)} chars) in {t_summary:.3f}s")
            time.sleep(4.0)

        # Questions for this PDF
        pdf_questions = [q for q in questions if q["pdf"] == pdf_name]
        for q in pdf_questions:
            qid = q["question_id"]
            if qid in completed_qids:
                logging.info(f"Skipping already-completed question: {qid}")
                continue

            q_text = q["question"]
            q_type = q.get("question_type", "factual")
            expected = q["expected_answer"]

            logging.info(f"Running [{qid}] ({q_type}): {q_text}")

            # Audio synthesis (offline)
            audio_path = AUDIO_DIR / f"{qid}.wav"
            synthesize_wav_offline(q_text, audio_path)

            # Stage 3: Audio Understanding & Query Pipeline
            t0 = time.perf_counter()
            try:
                model_answer = call_with_retry(main.process_query_with_llm, summary, str(audio_path))
            except Exception as e:
                logging.error(f"Error answering {qid}: {e}")
                model_answer = f"ERROR: {e}"
            t_qa = time.perf_counter() - t0
            stage_timings["audio_qa_inference"].append(t_qa)

            # Pacing delay between Q&A and Judge
            time.sleep(4.0)

            # Stage 4: Judge scoring
            judge_res = score_with_judge(q_text, expected, model_answer, q_type, judge_model)
            logging.info(f"[{qid}] Score: {judge_res['score']} | Justification: {judge_res['justification']}")

            res_entry = {
                "pdf": pdf_name,
                "question_id": qid,
                "question_type": q_type,
                "question": q_text,
                "expected_answer": expected,
                "model_answer": model_answer,
                "latency_extract_sec": t_extract,
                "latency_summary_sec": t_summary,
                "latency_audio_qa_sec": t_qa,
                "score": judge_res["score"],
                "evidence_span": judge_res["evidence_span"],
                "justification": judge_res["justification"]
            }
            results.append(res_entry)
            completed_qids.add(qid)

            # Checkpoint immediately to disk
            with open(checkpoint_file, "w", encoding="utf-8") as f:
                json.dump({"results": results}, f, indent=2)

            # Pacing delay between questions
            time.sleep(4.0)

    # ── Compute Aggregated Metrics ─────────────────────────────────────────────
    factual_results = [r for r in results if r["question_type"] == "factual"]
    adv_results = [r for r in results if r["question_type"] == "adversarial"]

    factual_points = sum(r["score"] for r in factual_results)
    factual_max = len(factual_results) * 2 if factual_results else 1
    factual_accuracy = (factual_points / factual_max) * 100

    adv_points = sum(r["score"] for r in adv_results)
    adv_max = len(adv_results) * 2 if adv_results else 1
    hallucination_resistance = (adv_points / adv_max) * 100

    total_points = sum(r["score"] for r in results)
    total_max = len(results) * 2 if results else 1
    overall_accuracy = (total_points / total_max) * 100

    per_pdf_stats = {}
    for p in pdfs:
        p_res = [r for r in results if r["pdf"] == p]
        p_fact = [r for r in p_res if r["question_type"] == "factual"]
        p_adv = [r for r in p_res if r["question_type"] == "adversarial"]
        
        f_pts = sum(r["score"] for r in p_fact)
        f_max = len(p_fact) * 2 if p_fact else 1
        
        a_pts = sum(r["score"] for r in p_adv)
        a_max = len(p_adv) * 2 if p_adv else 1

        per_pdf_stats[p] = {
            "factual_accuracy": round((f_pts / f_max) * 100, 1),
            "factual_counts": {
                "score_2": sum(1 for r in p_fact if r["score"] == 2),
                "score_1": sum(1 for r in p_fact if r["score"] == 1),
                "score_0": sum(1 for r in p_fact if r["score"] == 0),
                "total": len(p_fact)
            },
            "hallucination_resistance": round((a_pts / a_max) * 100, 1),
            "adversarial_counts": {
                "score_2": sum(1 for r in p_adv if r["score"] == 2),
                "score_1": sum(1 for r in p_adv if r["score"] == 1),
                "score_0": sum(1 for r in p_adv if r["score"] == 0),
                "total": len(p_adv)
            }
        }

    qa_times = [r["latency_audio_qa_sec"] for r in results if "latency_audio_qa_sec" in r]
    ext_times = stage_timings["pdf_extraction"]
    sum_times = [t for t in stage_timings["summarization"] if t > 0]

    def calc_stats(times):
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

    latency_stats = {
        "pdf_extraction": calc_stats(ext_times),
        "summarization": calc_stats(sum_times),
        "audio_qa_inference": calc_stats(qa_times),
        "text_to_speech": {
            "status": "SKIPPED",
            "reason": "Google Cloud Text-to-Speech credentials not configured"
        }
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = EVAL_DIR / f"results_{timestamp}.json"
    latest_file = EVAL_DIR / "results_latest.json"

    payload = {
        "timestamp": timestamp,
        "total_questions": len(results),
        "factual_questions": len(factual_results),
        "adversarial_questions": len(adv_results),
        "metrics": {
            "overall_accuracy_pct": round(overall_accuracy, 1),
            "factual_accuracy_pct": round(factual_accuracy, 1),
            "hallucination_resistance_pct": round(hallucination_resistance, 1),
            "raw_counts": {
                "score_2": sum(1 for r in results if r["score"] == 2),
                "score_1": sum(1 for r in results if r["score"] == 1),
                "score_0": sum(1 for r in results if r["score"] == 0)
            }
        },
        "per_pdf_stats": per_pdf_stats,
        "latency_stats": latency_stats,
        "results": results
    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    logging.info(f"Evaluation complete! Results saved to {out_file.name}")
    print("\n" + "="*60)
    print("EVALUATION HARNESS SUMMARY")
    print("="*60)
    print(f"Total Questions Evaluated:    {len(results)}")
    print(f"Factual Accuracy:             {factual_accuracy:.1f}%")
    print(f"Hallucination Resistance:     {hallucination_resistance:.1f}%")
    print(f"Combined Benchmark:           {overall_accuracy:.1f}%")
    print("-" * 60)
    print("Latency Benchmarks:")
    print(f"  PDF Extraction:             mean={latency_stats['pdf_extraction']['mean']}s | p95={latency_stats['pdf_extraction']['p95']}s")
    print(f"  Summarization:              mean={latency_stats['summarization']['mean']}s | p95={latency_stats['summarization']['p95']}s")
    print(f"  Multimodal Audio Q&A:       mean={latency_stats['audio_qa_inference']['mean']}s | p95={latency_stats['audio_qa_inference']['p95']}s")
    print(f"  TTS Synthesis:              SKIPPED (No GCP credentials)")
    print("="*60)


if __name__ == "__main__":
    main_eval()
