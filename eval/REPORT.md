# Empirical Evaluation Report: Multimodal Document Q&A Pipeline

**Repository:** `HiteshReddy2002/speech-and-text-conversion-sentimentanalysis-api`  
**Evaluation Date:** October 2026  
**Auditor:** Automated Agentic Evaluation Harness (Reproducible Benchmark)  
**Model Under Test:** `gemini-3.1-flash-lite` (Active Gemini multimodal API endpoint)  
**Ground Truth & Dataset Disclosure:** The evaluation PDF documents and test question-answer pairs were agent-generated and human-reviewed/approved by the repository owner before evaluation execution.

---

## 1. Executive Summary

This report establishes the first reproducible, transparent empirical benchmark for the `speech-and-text-conversion-sentimentanalysis-api` repository. Prior README claims asserted an unverified **"92% accuracy"**. 

Our evaluation demonstrates that **the 92% accuracy claim does NOT hold up under rigorous testing**:
- **Factual Accuracy:** **66.7%** (5/9 exact full credit, 2/9 partial credit, 2/9 missed/incomplete).
- **Hallucination Resistance:** **100.0%** (3/3 unanswerable/adversarial questions correctly resisted without fabricating facts).
- **Combined Overall Benchmark:** **75.0%**.
- **End-to-End Latency:** Mean audio query inference was **27.18s** (p95: **110.45s**), with initial document summarization averaging **13.29s** (p95: **24.05s**) and local PyMuPDF extraction taking **0.004s**.
- **Root Cause of Accuracy Gap:** The API's `/upload` endpoint passes only a generated `book_summary` into `process_query_with_llm` rather than the complete extracted document text or chunked embeddings. Granular figures and secondary bounds (e.g., upper systolic limits, clinical trial halting thresholds) omitted during the summarization stage cannot be answered during the spoken query stage.

---

## 2. Evaluation Methodology

### 2.1 Test Corpus & Dataset
The repository's `uploads/` folder contained no historical files following credential security remediation. Three multi-page domain-specific technical reference documents were generated in `eval/data/`:
1. `cloud_data_lakehouse_architecture.pdf`: Apache Iceberg v2, Kafka ingestion SLAs, GCS tiering, CMEK KMS rotation.
2. `clinical_cardiology_trial_protocol.pdf`: Phase IIb Cardiovastin trial, sample size, SBP inclusion thresholds, DSMB halting criteria.
3. `fintech_payment_security_spec.pdf`: TLS 1.3, HMAC-SHA256 signatures, timestamp skew rejection, chargeback evidence SLAs.

A balanced evaluation dataset of 12 questions was evaluated across the 3 documents:
- **9 Factual Questions:** Concrete ground-truth metrics, thresholds, or configurations directly present in the source text.
- **3 Adversarial / Unanswerable Questions:** Inquiries requesting information absent from the documents (e.g., cloud budgets, pediatric dosages, interchange fees) to measure hallucination resistance.

### 2.2 Execution Pipeline
Every question followed the repository's native execution path:
1. `extract_text_from_pdf`: PyMuPDF text extraction.
2. `summarize_book`: Initial document summarization via Gemini API.
3. **Deterministic Audio Input:** Each question was synthesized offline to a standard 16-bit PCM WAV file via Windows `System.Speech` before test execution, ensuring 100% deterministic acoustic inputs.
4. `process_query_with_llm`: Spoken WAV audio transmitted as `inline_data` alongside document summary context.
5. `text_to_speech`: **Skipped** (Google Cloud Text-to-Speech credentials were not present in the local environment; skipped cleanly without simulation).

### 2.3 LLM-as-Judge Rubric & Audit Trail
Adhering to [eval/RUBRIC.md](file:///C:/Users/hites/.gemini/antigravity-ide/scratch/speech-and-text-conversion-sentimentanalysis-api/eval/RUBRIC.md):
- **Score 2 (Full Credit):** Factually exact and complete; for adversarial questions, explicitly declining to answer.
- **Score 1 (Partial Credit):** Substantially correct with minor omissions or slight rounding.
- **Score 0 (No Credit):** Factually incorrect, contradictory, or hallucinated.
- **Evidence Requirement:** The judge must quote the exact span from the model answer that justifies the rating.

All raw outputs, per-stage timestamps, and judge justification spans are preserved in `eval/results_latest.json`.

### 2.4 Explicit Scoring Formulas

Each item is evaluated on a 3-point scale ($S \in \{0, 1, 2\}$) with a maximum of 2 points per item:

- **Factual Accuracy Formula:**
  $$\text{Factual Accuracy} = \frac{\sum_{i=1}^{N_{\text{factual}}} S_i}{2 \times N_{\text{factual}}} = \frac{(5 \times 2) + (2 \times 1) + (2 \times 0)}{2 \times 9} = \frac{10 + 2 + 0}{18} = \frac{12}{18} \approx 66.7\%$$
  *(5/9 items scored 2, 2/9 items scored 1, 2/9 items scored 0)*

- **Hallucination Resistance Formula:**
  $$\text{Hallucination Resistance} = \frac{\sum_{j=1}^{N_{\text{adversarial}}} S_j}{2 \times N_{\text{adversarial}}} = \frac{(3 \times 2) + (0 \times 1) + (0 \times 0)}{2 \times 3} = \frac{6}{6} = 100.0\%$$
  *(3/3 unanswerable items scored 2 by properly declining or identifying missing context)*

- **Combined Overall Benchmark Formula:**
  $$\text{Combined Benchmark} = \frac{\sum_{k=1}^{N_{\text{total}}} S_k}{2 \times N_{\text{total}}} = \frac{12 + 6}{18 + 6} = \frac{18}{24} = 75.0\%$$

---

## 3. Benchmark Results

### 3.1 Accuracy & Robustness Summary

| Metric | Score / Rate | Breakdown | Status |
|:---|:---:|:---|:---:|
| **Factual Accuracy** | **66.7%** | 5/9 exact (Score 2), 2/9 partial (Score 1), 2/9 missed (Score 0) | **Refutes 92% claim** |
| **Hallucination Resistance** | **100.0%** | 3 resisted (Score 2), 0 hedged (Score 1), 0 hallucinated (Score 0) | **Excellent** |
| **Combined Benchmark** | **75.0%** | 8 Full Credit, 2 Partial Credit, 2 No Credit (Total 18/24 pts) | **Realistic baseline** |

### 3.2 Accuracy Breakdown by Document

| Test Document | Factual Accuracy | Hallucination Resistance | Combined Score | Key Failure Mode |
|:---|:---:|:---:|:---:|:---|
| `clinical_cardiology_trial_protocol.pdf` | 33.3% (2/6 pts) | 100.0% (2/2 pts) | **50.0%** | Omitted SBP upper bound (179 mmHg); summary missed 2.5% halting rule |
| `cloud_data_lakehouse_architecture.pdf` | 83.3% (5/6 pts) | 100.0% (2/2 pts) | **87.5%** | Correctly retrieved Kafka 500ms SLA & 90-day CMEK; omitted "v2" table version |
| `fintech_payment_security_spec.pdf` | 83.3% (5/6 pts) | 100.0% (2/2 pts) | **87.5%** | Correctly retrieved TLS 1.3 & 14-day SLA; hedged on HTTP 401 status code |

---

## 4. Latency Performance

| Pipeline Stage | Implementation | Mean Latency | p95 Latency | Min | Max |
|:---|:---|:---:|:---:|:---:|:---:|
| **1. PDF Text Extraction** | Local PyMuPDF (`fitz`) | **0.004s** | **0.005s** | 0.003s | 0.005s |
| **2. Document Summarization** | Gemini API (`summarize_book`) | **13.289s** | **24.049s** | 1.354s | 24.049s |
| **3. Multimodal Audio Q&A** | Gemini inline audio (`process_query_with_llm`) | **27.179s** | **110.454s** | 4.680s | 110.454s |
| **4. Speech Synthesis (TTS)** | Google Cloud Text-to-Speech | *SKIPPED* | *SKIPPED* | *N/A* | *N/A* |

*Note: Multimodal Audio Q&A latency includes network transport and Gemini multimodal speech decoding. High max latency (110.45s) reflects free-tier pacing and exponential backoff.*

---

## 5. Itemized Audit Trail (All 12 Questions)

| Question ID | Type | Question Snippet | Expected Ground Truth | Model Answer Excerpt | Score | Quoted Evidence Span / Justification |
|:---:|:---:|:---|:---|:---|:---:|:---|
| **Q-CLIN-01** | Factual | Product name and code? | `Cardiovastin (CV-882)` | *"Cardiovastin, also identified by the code CV-882."* | **2** | *"The investigational product in this trial is Cardiovastin, also identified by the code CV-882."* |
| **Q-CLIN-03** | Factual | Screening resting SBP range? | `140 mmHg to 179 mmHg` | *"corresponds to a resting systolic blood pressure of 140 mmHg or higher."* | **0** | Omitted upper bound (179 mmHg); incomplete clinical range. |
| **Q-CLIN-06** | Factual | Halting threshold for Grade 3 hypotension? | `Exceeding 2.5% in any active arm` | *"the summary does not specify the exact blood pressure threshold for the halting criteria."* | **0** | Metric was omitted during summarization step; model claimed document lacked data. |
| **Q-CLIN-ADV-01** | Adversarial | Pediatric dosage under 12? | `Not mentioned (trial is adults 35-75)` | *"study is focused on adults... does not include information regarding pediatric use"* | **2** | Properly refused to hallucinate unmentioned pediatric dosage. |
| **Q-DLH-01** | Factual | Table format in Gold layer? | `Apache Iceberg v2` | *"engineering standard uses Apache Iceberg tables."* | **1** | Identified Apache Iceberg; omitted "v2" specification. |
| **Q-DLH-02** | Factual | Ingestion SLA for Kafka events? | `Under 500 milliseconds (p95)` | *"Kafka-based streaming with a latency of less than 500 milliseconds"* | **2** | Fully accurate latency SLA. |
| **Q-DLH-06** | Factual | CMEK rotation frequency? | `Automatically every 90 days` | *"customer-managed encryption keys (CMEK) are rotated every 90 days."* | **2** | Exact match on 90-day key rotation cycle. |
| **Q-DLH-ADV-01** | Adversarial | Annual infrastructure budget? | `Not mentioned` | *"does not mention a specific dollar amount for the annual cloud infrastructure budget."* | **2** | Correctly stated budget is not provided. |
| **Q-FIN-01** | Factual | Mandated TLS version? | `TLS version 1.3` | *"TLS 1.3 encryption is required for all API traffic"* | **2** | Exact match on security protocol version. |
| **Q-FIN-03** | Factual | Maximum timestamp skew? | `300 seconds (5 minutes)` | *"standard specifies a 5-minute window... does not explicitly state a 401 error"* | **1** | Identified 5-minute duration; hedged unnecessarily on HTTP 401 status. |
| **Q-FIN-06** | Factual | Evidence submission window? | `14 calendar days` | *"merchants have 14 days to submit evidence (rebuttal documentation)"* | **2** | Exact match on chargeback SLA. |
| **Q-FIN-ADV-01** | Adversarial | Mastercard interchange fee? | `Not mentioned` | *"does not contain information regarding transaction fees for Mastercard"* | **2** | Refused to fabricate financial fee schedule. |

---

## 6. Limitations & Threats to Validity

1. **Sample Size:** Benchmarked against 12 representative items (9 factual, 3 adversarial) across 3 distinct technical domains to strictly respect Google AI Studio free-tier quotas. While statistically informative of architecture bottlenecks, a larger 100+ sample run would tighten confidence intervals.
2. **Judge Model Bias:** Evaluation was judged using `gemini-3.1-flash-lite`, the same model family as the pipeline under test. To mitigate bias, strict evidence span quotes and ground-truth comparisons were enforced.
3. **Architecture Bottleneck:** The primary source of error is **not speech recognition or LLM comprehension**, but rather **intermediate context compression**: passing `book_summary` into the query prompt instead of the full extracted text.
4. **TTS Measurement Omission:** Google Cloud Text-to-Speech was not configured locally; speech synthesis latency is marked as skipped and must be evaluated separately in an environment with active GCP credentials.

---

## 7. Architectural Recommendations

To elevate factual accuracy from 66.7% to >90%:
1. **Bypass Intermediate Summarization for Queries:** Pass the full extracted text (or chunked vector retrieved spans) directly into `process_query_with_llm`, rather than compressing the document into an executive summary first.
2. **System Prompt Tuning:** Instruct the audio Q&A prompt to quote exact numbers, upper/lower bounds, and version qualifiers when answering numerical or technical questions.
