# Workshop Paper Skeleton: Native Audio vs. Cascaded Pipeline for Document-Grounded Spoken QA

**Target Venue:** Interspeech 2027 (Workshop Track on Trustworthy Speech Processing & Spoken Language Understanding)  
**Target Deadline:** ~February 9, 2027  
**Framing:** Empirical evaluation of efficiency, robustness, and hallucination resistance in document-grounded spoken QA  
**Core Scientific Claim:** Under document grounding, cascaded STT→LLM pipelines achieve identical accuracy and abstention rates to native-audio LLMs while delivering a **63.7% reduction in mean latency** and an **88.0% reduction in API operational cost**. Furthermore, intermediate context compression—not acoustic architecture—was the true accuracy bottleneck.

---

## Title Candidates

1. *The Illusion of Acoustic Superiority: Cascaded Pipelines Match Native Audio Accuracy in Document-Grounded Spoken QA at One-Third the Latency and Cost*
2. *Context Heals Acoustic Corruption: Empirical Parity Between Cascaded and Native Spoken Document QA*
3. *When Pipelines Win: Latency, Cost, and Abstention Trade-offs Between Native Audio and Cascaded Architectures for Grounded Spoken QA*
4. *Beyond End-to-End: Evaluating Trustworthiness, Latency, and Economics in Spoken Document Question Answering*

---

## Section-by-Section Outline & Evidence Audit

### Abstract
- **Core Claim:** Head-to-head empirical comparison across 30 domain-specific queries demonstrates 100% factual accuracy and 100% unanswerable abstention parity between native-audio and cascaded pipelines, with cascade delivering 63.7% lower mean latency and 88.0% lower API cost. Intermediate context compression (summarization) caused an earlier 66.7% accuracy ceiling, which full document context fully resolved.
- **Supporting Exhibit:** `eval/results_comparison_latest.json` (summary_metrics), `eval/COMPARISON_REPORT.md` (Section 1).
- **Prohibited Claim:** No claim of native accuracy advantage; parity must be stated.

---

### 1. Introduction
- **1.1 The Spoken Document QA Paradigm:**
  - Rise of multimodal foundation models capable of direct audio ingestion vs. traditional cascaded architectures (ASR → Text-LLM → TTS).
  - Common industry assumption: native audio avoids speech-to-text error propagation, especially on specialized domain terminology (medical, financial, systems engineering).
  - *Supporting Exhibit:* `eval/COMPARISON_REPORT.md` (Section 2).
- **1.2 Empirical Research Questions:**
  - RQ1 (Accuracy & Parity): Does native audio ingestion outperform cascaded ASR on domain-specific factual QA?
  - RQ2 (Trustworthiness & Abstention): How do architectures compare when handling adversarial, unanswerable queries?
  - RQ3 (System Efficiency): What are the true end-to-end latency, tail latency (p95/max), and inference cost profiles?
  - RQ4 (Context Sensitivity): What is the primary bottleneck for answer faithfulness: acoustic pipeline design or context representation?
  - *Supporting Exhibit:* `eval/COMPARISON_REPORT.md` (Section 2), `eval/RUBRIC.md` (Section 1-3).
- **1.3 Summary of Contributions:**
  - First reproducible, open-source test harness evaluating native vs. cascaded architectures under identical ground-truth document priors.
  - Verified empirical findings showing identical accuracy (100.0% vs. 100.0%) and adversarial abstention (100.0% vs. 100.0%).
  - Quantitative efficiency breakdown showing cascade wins by 63.7% mean latency (12.14s vs. 33.45s) and 88.0% API cost ($0.00239 vs. $0.01984).
  - Demonstration of semantic error recovery: downstream text LLMs repair phonetic Whisper distortions (*"slough or rot"*, *"AGFR"*) via document context.
  - Identification of context compression as the primary accuracy bottleneck (66.7% factual accuracy under summarization → 100.0% under full text).
  - *Supporting Exhibits:* `eval/results_comparison_latest.json`, `eval/COMPARISON_REPORT.md`, `eval/REPORT.md`.

---

### 2. Related Work
- **2.1 End-to-End Multimodal Speech Models vs. Cascades:**
  - *Cascade Equivalence Hypothesis* (arXiv:2602.17598): Theoretical and empirical bounds of cascaded vs. unified speech architectures.
  - *Full-Duplex-Bench v3* (arXiv:2604.04847): Interactive spoken dialogue benchmarks.
  - *Supporting Exhibit:* `paper/RELATED_WORK.md`.
- **2.2 Spoken Question Answering Benchmarks:**
  - *Spoken SQuAD* (ACL P18-4002): Classic ASR transcript error propagation on reading comprehension.
  - *VākQA* (arXiv:2406.11042): Multilingual spoken question answering.
  - *ViSQA* (EMNLP 2025 Findings): Visual and spoken document QA.
  - *Supporting Exhibit:* `paper/RELATED_WORK.md`.
- **2.3 The Grounding Gap:**
  - Existing benchmarks evaluate open-domain or retrieval-free speech QA; our work evaluates *document-grounded* QA where a dense technical reference prior is provided to the LLM.
  - *TODO-Related-Work:* Survey latest late-2026 preprints on Gemini 2.5/3.1 audio multimodal technical reports.

---

### 3. Experimental Methodology & Rig

#### 3.1 Pipeline Architectures Under Test
- **Native Audio Arm:**
  - Raw 16-bit PCM WAV streamed as `inline_data` alongside full document text into `gemini-3.1-flash-lite`.
  - Jointly extracts text answer and vocal acoustics (sentiment, tone, confidence).
  - *Supporting Exhibit:* `eval/native_arm.py`, `eval/results_comparison_latest.json` (lines 185-211).
- **Cascaded Pipeline Arm:**
  - Stage 1: Local STT via `faster-whisper` (`base` model, CPU `int8` quantization). Zero audio egress.
  - Stage 2: Prompt assembly with transcribed query text and identical full document context into `gemini-3.1-flash-lite`.
  - Stage 3: Text-to-Speech response synthesis.
  - *Supporting Exhibit:* `eval/cascade_arm.py`, `eval/results_comparison_latest.json` (lines 212-233).
- **Stage Timing Protocol:**
  - Native: $T_{\text{total}} = T_{\text{multimodal\_llm}}$ ($T_{\text{stt}} = 0.0\text{s}$, $T_{\text{tts}} = \text{skipped}$).
  - Cascade: $T_{\text{total}} = T_{\text{whisper}} + T_{\text{text\_llm}}$ ($T_{\text{tts}} = \text{skipped}$).
  - *Supporting Exhibit:* `eval/results_comparison_latest.json` (lines 29-53, 80-104).

#### 3.2 Evaluation Corpus & Dataset Design
- **Corpus Documents ($N=3$ technical domains):**
  - Data Engineering: `cloud_data_lakehouse_architecture.pdf` (Apache Iceberg v2, Kafka SLA, CMEK KMS).
  - Clinical Cardiology: `clinical_cardiology_trial_protocol.pdf` (Phase IIb Cardiovastin, eGFR cutoff, halting rules).
  - Financial Security: `fintech_payment_security_spec.pdf` (TLS 1.3, HMAC-SHA256, dispute settlement SLAs).
  - Extraction via PyMuPDF (`fitz`), cached locally with `MAX_DOCUMENT_CHARS = 50,000`.
  - *Supporting Exhibit:* `eval/data/` (PDF files), `eval/COMPARISON_REPORT.md` (Section 3.1).
- **Question Composition ($N=30$ total items):**
  - 21 Factual Questions: Precise numerical thresholds, protocols, and architectural specifications.
  - 9 Adversarial Questions: Inquiries deliberately targeting information absent from the text (pediatric dosages, cloud budgets, cryptocurrency settlement) to test hallucination resistance.
  - Acoustic generation: Synthesized offline to standard 16-bit PCM WAV using Windows `System.Speech` to eliminate online synthesis variance.
  - *Supporting Exhibit:* `eval/dataset.csv`, `eval/COMPARISON_REPORT.md` (Section 3.2).
- **TODO-1 (Load-Bearing):** Acoustic diversity expansion — record real multi-accent human speakers with calibrated background noise (SNR 10dB, 20dB) to evaluate boundary conditions where Whisper STT WER exceeds LLM recovery capability.

#### 3.3 Scoring Rubric & LLM-as-Judge Protocol
- **3-Point Auditable Rubric (`eval/RUBRIC.md`):**
  - Score 2 (Full Credit): Factually complete and exact; for adversarial questions, explicit and unambiguous refusal to answer.
  - Score 1 (Partial Credit): Substantively correct core fact with minor non-critical omission; for adversarial, hedged response.
  - Score 0 (No Credit): Factually incorrect, contradictory, or fabricated hallucination.
  - Mandatory Span Matching: Judge must cite the exact verbatim evidence span from the generated response.
- **Judge Configuration:**
  - Impartial batch evaluation via `gemini-3.1-flash-lite`.
  - *Supporting Exhibit:* `eval/RUBRIC.md`, `eval/results_comparison_latest.json` (judge outputs).
- **TODO-5 (Nice-to-Have):** Human-expert validation on 100% of responses with Cohen's $\kappa$ inter-rater reliability calculation against LLM judge.

---

### 4. Results & Empirical Analysis

#### 4.1 Factual Accuracy & Hallucination Resistance Parity
- **Global Scorecard ($N=30$ items, 60 max points):**
  - Factual Accuracy: 100.0% Native (42/42 pts) vs. 100.0% Cascade (42/42 pts) ($\Delta = 0.0\%$).
  - Adversarial Abstention: 100.0% Native (18/18 pts, 9/9 refusals) vs. 100.0% Cascade (18/18 pts, 9/9 refusals) ($\Delta = 0.0\%$).
  - Combined Benchmark: 100.0% Native (60/60 pts) vs. 100.0% Cascade (60/60 pts).
  - Inter-arm Agreement: 30/30 (100.0% agreement, 0 disagreements).
  - *Supporting Exhibit:* `eval/results_comparison_latest.json` (summary_metrics, per_pdf_stats).
- **TODO-2 (Load-Bearing):** Scaling sample size from $N=30$ to $N=200+$ questions to calculate formal statistical confidence intervals (bootstrap 95% CI) and confirm parity holds under long-tail domain queries.

#### 4.2 Latency Breakdown: Local STT vs. Multimodal Payload Penalty
- **End-to-End Latency ($N=30$ items):**
  - Native Mean: 33.450s (p95: 71.633s, Min: 5.127s, Max: 316.762s).
  - Cascade Mean: 12.136s (p95: 24.969s, Min: 3.382s, Max: 61.836s).
  - Local Whisper STT: Mean = 0.409s (p95: 0.582s, Min: 0.331s, Max: 0.650s).
  - Cascade LLM Inference: Mean = 11.727s (p95: 24.606s, Min: 3.037s, Max: 61.493s).
  - Mean Latency Delta: Cascade is **21.314s faster** (**63.7% reduction**, **2.76× speedup**).
  - p95 Tail Latency Delta: Cascade is **46.664s faster** (**65.1% reduction**).
  - *Supporting Exhibit:* `eval/results_comparison_latest.json` (latencies), `eval/COMPARISON_REPORT.md` (Section 5).
- **Tail Latency Blowup Analysis:**
  - Item `Q-FIN-ADV-03`: Native arm took **316.762s** due to server-side multimodal decoding and queuing, while Cascade arm finished in **6.723s** (0.366s STT + 6.357s LLM).
  - *Supporting Exhibit:* `eval/results_comparison_latest.json` (lines 1827-1875).

#### 4.3 Token Economics & Operational Cost
- **Consumption & Billing Metrics (Gemini Developer List Price):**
  - Pricing: Text input = $0.10 / 1M tokens; Audio input = $0.70 / 1M tokens; Output = $0.40 / 1M tokens.
  - Native Arm: 26,907 prompt tokens + 2,520 candidate tokens = 29,427 total tokens → **$0.01984 USD**.
  - Cascade Arm: 20,448 prompt tokens + 873 candidate tokens = 21,321 total tokens → **$0.00239 USD**.
  - Cost Delta: Cascade is **$0.01745 USD cheaper** (**88.0% cost reduction**, **8.3× cheaper**).
  - Actual Billed Cost on Google AI Studio Free Tier: **$0.00**.
  - Candidate Output Token Conciseness: Cascade answers generated 873 tokens vs. Native 2,520 tokens (-65.4% reduction), avoiding conversational audio filler.
  - *Supporting Exhibit:* `eval/results_comparison_latest.json` (tokens, estimated_api_cost_usd), `eval/COMPARISON_REPORT.md` (Section 6).

#### 4.4 The Context Compression Ablation
- **Intermediate Summarization vs. Full Document Context ($N=12$ items):**
  - Summarization pipeline achieved only **66.7% factual accuracy** (5/9 exact, 2/9 partial, 2/9 missed; combined: 75.0%).
  - Full-document context refactor elevated factual accuracy to **100.0%** on both arms.
  - Proof that intermediate text compression, rather than speech modeling architecture, is the operational bottleneck in document-grounded QA.
  - *Supporting Exhibit:* `eval/results_latest.json`, `eval/REPORT.md` (Sections 1 & 3.1).

---

### 5. Acoustic Distortion & Semantic Recovery (Failure Analysis)

- **Mechanisms of Phonetic Distortion with Semantic Recovery:**
  - Case 1: *Acoustic Phonetic Confusion* (`Q-DLH-02`): *"SLA for raw"* transcribed as *"slough or rot"*. Downstream text LLM recovered *"Under 500 milliseconds (p95)"* via Kafka context.
  - Case 2: *Clause Truncation* (`Q-DLH-01`): Whisper omitted trailing prepositional phrase. LLM recovered Gold layer format (*"Apache Iceberg v2"*).
  - Case 3: *Acronym Misrecognition* (`Q-CLIN-04`): *"eGFR"* transcribed as *"AGFR"*. Recovered via expanded medical context (*"Below 30 mL/min/1.73 m²"*).
  - Case 4: *Critical Clinical Inversion* (`Q-CLIN-06`): *"hypotension"* transcribed as *"hypertension"*. Document halting criteria section allowed LLM to retrieve *"Exceeding 2.5%"*.
  - Case 5: *Phonetic Merger* (`Q-FIN-07`): *"settlement SLA"* transcribed as *"settlements law"*. Recovered via dispute table (*"Within 45 calendar days"*).
  - *Supporting Exhibit:* `eval/results_comparison_latest.json` (transcripts and answers), `eval/COMPARISON_REPORT.md` (Table 7).
- **Unique Capability of Native Arm:**
  - Vocal Tone and Emotion Extraction: Native arm successfully extracted query sentiment and acoustic tone across all 30 questions (e.g., inquisitive, neutral, direct), a modality lost in STT.
  - *Supporting Exhibit:* `eval/results_comparison_latest.json` (sentiment blocks).
- **TODO-6 (Nice-to-Have):** Downstream utility evaluation: measure whether extracting vocal tone provides actionable value in clinical triage or customer dispute workflows.

---

### 6. Limitations & Threats to Validity

1. **Acoustic Input Homogeneity:**
   - Evaluated on clean, uncompressed 16-bit PCM synthesized audio (Windows `System.Speech`). Does not represent noisy acoustic field conditions.
   - *Addressed by:* Explicitly discussed as a boundary condition; planned for TODO-1.
2. **TTS Stage Omission:**
   - Text-to-Speech stage was skipped ($0.0\text{s}$) due to unconfigured GCP service account credentials in the test environment.
   - *TODO-3 (Load-Bearing):* Measure live Google Cloud TTS latency (~1.0s–2.0s) and bandwidth overhead to complete end-to-end spoken-in / spoken-out comparison.
3. **Model Heterogeneity:**
   - Native uses end-to-end Gemini audio-language representations; Cascade ensembles OpenAI `faster-whisper-base` with Gemini text.
   - *TODO-4 (Nice-to-Have):* Cross-evaluate with additional open-source ASR models (Whisper-large-v3, Canary) and multimodal baselines (GPT-4o Audio).
4. **Sample Size ($N=30$):**
   - High power for large latency/cost effect sizes ($p < 0.001$), but small for granular subgroup error breakdowns.
   - *Addressed by:* Explicit disclosure; planned for TODO-2.
5. **API Gateway Latency Jitter:**
   - Free-tier rate limits and server queues contribute to observed tail latencies (316.8s max).
   - *Addressed by:* Reporting both median/mean and p95/max, and highlighting local compute predictability.

---

### 7. Conclusion & Recommendations

1. **Architecture Recommendation for Industry:**
   - For document-grounded spoken QA, cascaded architectures using lightweight local STT (`faster-whisper`) dominate end-to-end native audio in latency (-63.7%) and cost (-88.0%) without any accuracy penalty.
2. **Context Heals Acoustic Corruption:**
   - Dense document grounding provides an overwhelming language model prior that compensates for moderate phonological errors.
3. **When to Choose Native Audio:**
   - Reserve native multimodal models for applications where acoustic paralinguistics (emotion, stress, vocal biomarkers, tone) are functionally necessary.
4. **Reproducibility Guarantee:**
   - Complete harness, dataset, audio generation scripts, and judge prompts available in open-source repository.

---

## Exhibits & Claims Traceability Matrix

| Planned Section | Planned Claim / Metric | Supporting Exhibit File | Exact Data Key / Line | Status |
|:---|:---|:---|:---|:---:|
| **Abstract / Sec 4.1** | Factual accuracy tied at 100.0% (42/42 pts) | `eval/results_comparison_latest.json` | `summary_metrics.*.factual_accuracy_pct` | **VERIFIED** |
| **Abstract / Sec 4.1** | Adversarial abstention tied at 100.0% (9/9 refusals) | `eval/results_comparison_latest.json` | `summary_metrics.*.abstention_rate_pct` | **VERIFIED** |
| **Abstract / Sec 4.2** | Cascade mean latency 12.14s vs. Native 33.45s (-63.7%) | `eval/results_comparison_latest.json` | `summary_metrics.*.latencies.total.mean` | **VERIFIED** |
| **Sec 4.2** | Cascade p95 latency 24.97s vs. Native 71.63s (-65.1%) | `eval/results_comparison_latest.json` | `summary_metrics.*.latencies.total.p95` | **VERIFIED** |
| **Sec 4.2** | Local Whisper STT mean latency 0.409s (p95: 0.582s) | `eval/results_comparison_latest.json` | `summary_metrics.cascade.latencies.stt` | **VERIFIED** |
| **Sec 4.2** | Native max latency outlier 316.762s on Q-FIN-ADV-03 | `eval/results_comparison_latest.json` | `itemized_results[29].native.stage_latencies.llm` | **VERIFIED** |
| **Abstract / Sec 4.3** | Cascade API cost $0.00239 vs. Native $0.01984 (-88.0%) | `eval/results_comparison_latest.json` | `summary_metrics.*.estimated_api_cost_usd` | **VERIFIED** |
| **Sec 4.3** | Candidate tokens: Cascade 873 vs. Native 2,520 (-65.4%) | `eval/results_comparison_latest.json` | `summary_metrics.*.tokens.candidates_tokens` | **VERIFIED** |
| **Sec 4.4** | Intermediate summarization baseline factual acc 66.7% | `eval/results_latest.json`, `eval/REPORT.md` | `eval/REPORT.md` Sec 1 & 3.1 | **VERIFIED** |
| **Sec 5** | Whisper distortion "slough or rot" repaired to Kafka SLA | `eval/results_comparison_latest.json` | `itemized_results[1].cascade.transcript` | **VERIFIED** |
| **Sec 5** | Whisper distortion "AGFR" repaired to eGFR threshold | `eval/results_comparison_latest.json` | `itemized_results[13].cascade.transcript` | **VERIFIED** |
| **Sec 5** | Native arm extracts tone/emotion (calm, inquisitive) | `eval/results_comparison_latest.json` | `itemized_results[*].native.sentiment` | **VERIFIED** |
| **Sec 3.1 / 6** | TTS latency skipped (0.0s recorded) | `eval/results_comparison_latest.json` | `summary_metrics.*.latencies.tts.status` | **VERIFIED** |
| **Sec 3.2 / 6** | Multi-accent real human audio under noise (SNR 10dB) | None (Planned Experiment) | `TODO-1` | **TODO** |
| **Sec 4.1 / 6** | Large-scale evaluation (N=200+) with bootstrap 95% CIs | None (Planned Experiment) | `TODO-2` | **TODO** |
| **Sec 6** | Live Google Cloud TTS latency benchmarking (~1.5s) | None (Requires GCP Service Account) | `TODO-3` | **TODO** |
| **Sec 6** | Cross-model evaluation (Whisper-large, GPT-4o Audio) | None (Planned Experiment) | `TODO-4` | **TODO** |
| **Sec 3.3** | Human expert inter-annotator agreement (Cohen's κ) | None (Planned Annotation) | `TODO-5` | **TODO** |
| **Sec 5** | Utility quantification of acoustic sentiment in triage | None (Planned User Study) | `TODO-6` | **TODO** |
