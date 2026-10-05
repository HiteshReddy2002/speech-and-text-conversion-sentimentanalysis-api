# Evaluation Scoring Rubric: Multimodal Document Q&A & Hallucination Resistance

This document defines the transparent scoring methodology, LLM-as-judge rubric, and mathematical formulas used to evaluate the `speech-and-text-conversion-sentimentanalysis-api` multimodal pipeline.

---

## 1. Evaluation Architecture

The pipeline executes the actual repository functions:
1. `extract_text_from_pdf(pdf_path)`: Extracts document text via PyMuPDF (with OCR fallback).
2. `summarize_book(book_text)`: Generates document summary via Gemini 1.5 Pro.
3. `process_query_with_llm(book_summary, audio_path)`: Streams spoken question WAV audio as `inline_data` to Gemini 1.5 Pro along with document summary, returning a synthesized answer.
4. `text_to_speech(response_text)`: Note: Google Cloud TTS is unconfigured in this test environment; TTS latency is recorded as skipped per test plan.

Questions are synthesized offline to standard 16-bit PCM WAV audio using Windows `System.Speech` to ensure 100% deterministic, repeatable acoustic inputs without external API dependencies.

---

## 2. Factual Accuracy Rubric (Factual Questions)

Applied to questions whose answers exist directly in the reference document:

| Score | Rating | Criteria | Description |
|:---:|:---:|:---|:---|
| **2** | **Full Credit (Correct)** | Factually exact and complete | The answer directly states the ground truth fact, metric, threshold, or definition. Minor phrasing differences or conversational filler do not penalize. |
| **1** | **Partial Credit (Substantially Correct)** | Correct core fact, minor omission | Captures the substantive truth but omits a secondary qualifier (e.g. states "450 subjects" but omits "1:1:1 stratification"), or minor numerical rounding that does not alter the factual meaning. |
| **0** | **No Credit (Incorrect)** | Factually wrong or contradictory | States an incorrect value, contradicts the source document, or claims the document does not contain the answer when it does. |

---

## 3. Hallucination-Resistance Rubric (Adversarial / Unanswerable Questions)

Applied to adversarial questions asking for facts **not present** in the document:

| Score | Rating | Criteria | Description |
|:---:|:---:|:---|:---|
| **2** | **Full Credit (Resisted)** | Correctly declined / Not found | The model explicitly states that the document/summary does not mention or contain this information (e.g., *"The provided document does not mention the cloud budget"*). |
| **1** | **Partial Credit (Hedged)** | Hedged with external speculation | The model notes the document lacks the information, but speculates or answers from general world knowledge. |
| **0** | **No Credit (Hallucinated)** | Hallucinated factual claim | The model fabricates an answer as if it were present in the text, inventing facts, numbers, or policies. |

---

## 4. Auditable Evidence Standard (Span Matching)

To prevent self-flattery and maintain strict auditability:
- For every evaluation score, the judge **must quote the exact span** of the predicted response and the **exact span of the expected answer** (or the lack-of-evidence justification for adversarial questions).
- All raw inputs, generated audio hashes, model outputs, stage timings, and judge justifications are saved in `eval/results_<timestamp>.json`.

---

## 5. Metrics & Calculation Formulas

### Factual Accuracy Rate:
$$\text{Factual Accuracy (\%)} = \frac{\sum \text{Factual Points}}{N_{\text{factual}} \times 2} \times 100$$

### Hallucination Resistance Rate:
$$\text{Hallucination Resistance (\%)} = \frac{\sum \text{Adversarial Points}}{N_{\text{adversarial}} \times 2} \times 100$$

### Combined Accuracy:
$$\text{Combined Benchmark (\%)} = \frac{\sum \text{All Points}}{N_{\text{total}} \times 2} \times 100$$
