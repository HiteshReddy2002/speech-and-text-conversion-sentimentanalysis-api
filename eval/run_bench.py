"""
Streamlined 12-Question Multimodal Benchmark (fits strictly within Gemini Free-Tier Daily Quota of 20 requests).
- 3 PDFs (1 summary each = 3 calls)
- 12 Audio Q&A questions (3 factual + 1 adversarial per PDF = 12 calls)
- 1 Single-Batch LLM-as-Judge evaluation call = 1 call
Total calls: 16 (strictly <= 20 daily quota)
"""

import os
import sys
import time
import json
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

BENCHMARK_ITEMS = [
    # PDF 1: Cloud Data Lakehouse
    {
        "pdf": "cloud_data_lakehouse_architecture.pdf",
        "question_id": "Q-DLH-01",
        "question_type": "factual",
        "question": "What table format is used for all transformed tables in the Gold analytical layer?",
        "expected_answer": "Apache Iceberg v2",
        "page_hint": "Page 2"
    },
    {
        "pdf": "cloud_data_lakehouse_architecture.pdf",
        "question_id": "Q-DLH-02",
        "question_type": "factual",
        "question": "What is the sustained ingestion SLA for raw transactional events captured from Kafka topics?",
        "expected_answer": "Under 500 milliseconds (p95)",
        "page_hint": "Page 1"
    },
    {
        "pdf": "cloud_data_lakehouse_architecture.pdf",
        "question_id": "Q-DLH-06",
        "question_type": "factual",
        "question": "How often are Customer-Managed Encryption Keys (CMEK) rotated?",
        "expected_answer": "Automatically every 90 days",
        "page_hint": "Page 2"
    },
    {
        "pdf": "cloud_data_lakehouse_architecture.pdf",
        "question_id": "Q-DLH-ADV-01",
        "question_type": "adversarial",
        "question": "What is the annual cloud infrastructure budget allocated for the Lakehouse cluster?",
        "expected_answer": "The document does not mention an annual cloud infrastructure budget.",
        "page_hint": "None (unanswerable)"
    },

    # PDF 2: Clinical Trial
    {
        "pdf": "clinical_cardiology_trial_protocol.pdf",
        "question_id": "Q-CLIN-01",
        "question_type": "factual",
        "question": "What is the investigational product name and code in the trial?",
        "expected_answer": "Cardiovastin (CV-882)",
        "page_hint": "Page 1"
    },
    {
        "pdf": "clinical_cardiology_trial_protocol.pdf",
        "question_id": "Q-CLIN-03",
        "question_type": "factual",
        "question": "What resting systolic blood pressure range is required at screening?",
        "expected_answer": "Between 140 mmHg and 179 mmHg",
        "page_hint": "Page 1"
    },
    {
        "pdf": "clinical_cardiology_trial_protocol.pdf",
        "question_id": "Q-CLIN-06",
        "question_type": "factual",
        "question": "What threshold of Grade 3 hypotension triggers the predefined study halting criteria?",
        "expected_answer": "Exceeding 2.5% in any active treatment arm",
        "page_hint": "Page 2"
    },
    {
        "pdf": "clinical_cardiology_trial_protocol.pdf",
        "question_id": "Q-CLIN-ADV-01",
        "question_type": "adversarial",
        "question": "What is the recommended pediatric dosage for Cardiovastin in children under 12 years old?",
        "expected_answer": "The document does not mention pediatric dosage; the trial is restricted to adults aged 35 to 75.",
        "page_hint": "None (unanswerable)"
    },

    # PDF 3: FinTech Security
    {
        "pdf": "fintech_payment_security_spec.pdf",
        "question_id": "Q-FIN-01",
        "question_type": "factual",
        "question": "Which version of TLS is required for payment authorization requests?",
        "expected_answer": "TLS version 1.3",
        "page_hint": "Page 1"
    },
    {
        "pdf": "fintech_payment_security_spec.pdf",
        "question_id": "Q-FIN-03",
        "question_type": "factual",
        "question": "What is the maximum permitted timestamp skew before a request is rejected with HTTP 401?",
        "expected_answer": "300 seconds (5 minutes)",
        "page_hint": "Page 1"
    },
    {
        "pdf": "fintech_payment_security_spec.pdf",
        "question_id": "Q-FIN-06",
        "question_type": "factual",
        "question": "How many calendar days do merchants have to submit rebuttal documentation for a chargeback?",
        "expected_answer": "Exactly 14 calendar days from the notification date",
        "page_hint": "Page 2"
    },
    {
        "pdf": "fintech_payment_security_spec.pdf",
        "question_id": "Q-FIN-ADV-01",
        "question_type": "adversarial",
        "question": "What is the interchange transaction fee charged for Mastercard debit cards?",
        "expected_answer": "The document does not mention interchange transaction fees.",
        "page_hint": "None (unanswerable)"
    }
]


def synthesize_wav_offline(text: str, output_path: Path) -> Path:
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
        raise RuntimeError(f"PowerShell audio synthesis failed: {result.stderr}")
    return output_path


def call_with_retry(fn, *args, max_retries=10, delay=10, **kwargs):
    for attempt in range(max_retries):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            err_str = str(e).lower()
            if "resource_exhausted" in err_str or "429" in err_str or "quota" in err_str:
                wait_time = min(90, delay * (attempt + 1))
                logging.warning(f"Rate limited (attempt {attempt+1}/{max_retries}). Backing off for {wait_time}s...")
                time.sleep(wait_time)
            else:
                logging.error(f"API call failed: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(delay)
    raise RuntimeError("Max retries exceeded.")


def run_benchmark():
    logging.info(f"Starting benchmark of {len(BENCHMARK_ITEMS)} items across 3 PDFs...")
    
    stage_timings = {
        "pdf_extraction": [],
        "summarization": [],
        "audio_qa_inference": []
    }
    
    doc_summaries = {}
    doc_extracted_text = {}
    results = []

    pdfs = sorted(list(set(item["pdf"] for item in BENCHMARK_ITEMS)))

    for pdf_name in pdfs:
        pdf_path = DATA_DIR / pdf_name
        logging.info(f"--- Processing {pdf_name} ---")

        # 1. Extraction
        t0 = time.perf_counter()
        extracted_text = main.extract_text_from_pdf(str(pdf_path))
        t_extract = time.perf_counter() - t0
        stage_timings["pdf_extraction"].append(t_extract)
        doc_extracted_text[pdf_name] = extracted_text
        logging.info(f"Extracted {len(extracted_text)} chars in {t_extract:.3f}s")

        # 2. Summarize (1 API call per PDF)
        t0 = time.perf_counter()
        summary = call_with_retry(main.summarize_book, extracted_text)
        t_summary = time.perf_counter() - t0
        stage_timings["summarization"].append(t_summary)
        doc_summaries[pdf_name] = summary
        logging.info(f"Summarized in {t_summary:.3f}s ({len(summary)} chars)")
        time.sleep(4.0)

        # Questions for this PDF
        pdf_items = [it for it in BENCHMARK_ITEMS if it["pdf"] == pdf_name]
        for it in pdf_items:
            qid = it["question_id"]
            q_text = it["question"]
            q_type = it["question_type"]
            expected = it["expected_answer"]

            logging.info(f"Answering [{qid}] ({q_type})...")
            wav_path = AUDIO_DIR / f"{qid}.wav"
            synthesize_wav_offline(q_text, wav_path)

            t0 = time.perf_counter()
            model_answer = call_with_retry(main.process_query_with_llm, summary, str(wav_path))
            t_qa = time.perf_counter() - t0
            stage_timings["audio_qa_inference"].append(t_qa)
            logging.info(f"Answered [{qid}] in {t_qa:.3f}s: {model_answer[:70]}...")

            results.append({
                "pdf": pdf_name,
                "question_id": qid,
                "question_type": q_type,
                "question": q_text,
                "expected_answer": expected,
                "page_hint": it["page_hint"],
                "model_answer": model_answer,
                "latency_extract_sec": round(t_extract, 3),
                "latency_summary_sec": round(t_summary, 3),
                "latency_audio_qa_sec": round(t_qa, 3)
            })
            time.sleep(4.0)

    # 3. Batch LLM-as-Judge Scoring (Exactly 1 API call for all 12 answers)
    logging.info("Executing Batch LLM-as-Judge evaluation on all 12 answers...")
    judge_prompt = """
You are an impartial, rigorous evaluation judge auditing an AI multimodal document Q&A assistant according to eval/RUBRIC.md.

Scoring Rules:
For factual questions:
- 2 = Correct: directly states the ground-truth fact/metric.
- 1 = Partial: correct substance with minor omission/imprecision.
- 0 = Incorrect: wrong, contradictory, or missed fact.

For adversarial questions (unanswerable):
- 2 = Resisted: explicitly states the document/summary does not mention or contain this info.
- 1 = Hedged: notes document lacks it, but speculates.
- 0 = Hallucinated: invents an answer claiming it was in the document.

You MUST provide an exact evidence quote span justifying every score.

Here are the Q&A pairs to evaluate:
"""
    for i, r in enumerate(results, 1):
        judge_prompt += f"""
--- Item {i} ---
ID: {r['question_id']}
Type: {r['question_type']}
Question: {r['question']}
Expected Ground Truth: {r['expected_answer']}
Model Answer:
\"\"\"{r['model_answer']}\"\"\"
"""

    judge_prompt += """
Respond ONLY with a JSON array containing an evaluation object for each item in order:
[
  {
    "question_id": "Q-DLH-01",
    "score": 2,
    "evidence_span": "<exact quote from model answer>",
    "justification": "<one sentence justification>"
  },
  ...
]
"""

    judge_model = genai.GenerativeModel(main.GEMINI_MODEL)
    judge_resp = call_with_retry(judge_model.generate_content, judge_prompt)
    raw_judge = judge_resp.text.strip()
    if raw_judge.startswith("```json"):
        raw_judge = raw_judge[7:]
    if raw_judge.startswith("```"):
        raw_judge = raw_judge[3:]
    if raw_judge.endswith("```"):
        raw_judge = raw_judge[:-3]
    raw_judge = raw_judge.strip()

    judge_scores = json.loads(raw_judge)
    score_map = {item["question_id"]: item for item in judge_scores}

    for r in results:
        j = score_map.get(r["question_id"], {"score": 0, "evidence_span": "N/A", "justification": "Missing judge score"})
        r["score"] = j["score"]
        r["evidence_span"] = j["evidence_span"]
        r["justification"] = j["justification"]

    # 4. Compute Metrics
    factual = [r for r in results if r["question_type"] == "factual"]
    adversarial = [r for r in results if r["question_type"] == "adversarial"]

    fact_pts = sum(r["score"] for r in factual)
    fact_max = len(factual) * 2
    factual_acc = (fact_pts / fact_max) * 100

    adv_pts = sum(r["score"] for r in adversarial)
    adv_max = len(adversarial) * 2
    hallucination_res = (adv_pts / adv_max) * 100

    total_pts = sum(r["score"] for r in results)
    total_max = len(results) * 2
    overall_acc = (total_pts / total_max) * 100

    per_pdf_stats = {}
    for p in pdfs:
        p_res = [r for r in results if r["pdf"] == p]
        p_fact = [r for r in p_res if r["question_type"] == "factual"]
        p_adv = [r for r in p_res if r["question_type"] == "adversarial"]

        f_pts = sum(r["score"] for r in p_fact)
        f_max = len(p_fact) * 2
        a_pts = sum(r["score"] for r in p_adv)
        a_max = len(p_adv) * 2

        per_pdf_stats[p] = {
            "factual_accuracy_pct": round((f_pts / f_max) * 100, 1),
            "factual_counts": {
                "score_2": sum(1 for r in p_fact if r["score"] == 2),
                "score_1": sum(1 for r in p_fact if r["score"] == 1),
                "score_0": sum(1 for r in p_fact if r["score"] == 0),
                "total": len(p_fact)
            },
            "hallucination_resistance_pct": round((a_pts / a_max) * 100, 1),
            "adversarial_counts": {
                "score_2": sum(1 for r in p_adv if r["score"] == 2),
                "score_1": sum(1 for r in p_adv if r["score"] == 1),
                "score_0": sum(1 for r in p_adv if r["score"] == 0),
                "total": len(p_adv)
            }
        }

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

    qa_times = [r["latency_audio_qa_sec"] for r in results]
    ext_times = stage_timings["pdf_extraction"]
    sum_times = stage_timings["summarization"]

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
        "model_used": main.GEMINI_MODEL,
        "total_questions": len(results),
        "factual_questions": len(factual),
        "adversarial_questions": len(adversarial),
        "metrics": {
            "overall_benchmark_pct": round(overall_acc, 1),
            "factual_accuracy_pct": round(factual_acc, 1),
            "hallucination_resistance_pct": round(hallucination_res, 1),
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

    print("\n" + "="*65)
    print("BENCHMARK EXECUTION REPORT")
    print("="*65)
    print(f"Model Evaluated:             {main.GEMINI_MODEL}")
    print(f"Total Questions:             {len(results)} (9 factual, 3 adversarial)")
    print(f"Factual Accuracy Rate:       {factual_acc:.1f}%")
    print(f"Hallucination Resistance:    {hallucination_res:.1f}%")
    print(f"Combined Benchmark:          {overall_acc:.1f}%")
    print("-" * 65)
    print("Latencies (seconds):")
    print(f"  PDF Extraction:            mean={latency_stats['pdf_extraction']['mean']}s | p95={latency_stats['pdf_extraction']['p95']}s")
    print(f"  Document Summarization:    mean={latency_stats['summarization']['mean']}s | p95={latency_stats['summarization']['p95']}s")
    print(f"  Multimodal Audio Q&A:      mean={latency_stats['audio_qa_inference']['mean']}s | p95={latency_stats['audio_qa_inference']['p95']}s")
    print(f"  TTS Synthesis:             SKIPPED (No GCP credentials)")
    print("="*65)

    return payload


if __name__ == "__main__":
    run_benchmark()
