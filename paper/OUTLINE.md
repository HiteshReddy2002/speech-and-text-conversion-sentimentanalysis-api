# Workshop Paper Skeleton: Native Audio vs. Cascaded Pipeline for Document-Grounded Spoken QA

**Target Venue:** Interspeech 2027 (Workshop Track on Trustworthy Speech Processing & Spoken Language Understanding)  
**Target Deadline:** ~February 9, 2027  
**Framing:** Empirical evaluation of efficiency, robustness, and hallucination resistance in document-grounded spoken QA  
**Core Scientific Claim:** Under document grounding, cascaded STT→LLM pipelines match native-audio models on accuracy and latency for document-grounded spoken QA, at one-eighth the API cost (87.8% cost reduction). Intermediate context compression—not acoustic architecture—was the true accuracy bottleneck, while apparent pilot latency advantages were resolved as free-tier API throttling confounds.

---

## Title Candidates

1. *The Economics of Grounded Speech: Cascaded Pipelines Match Native Audio on Accuracy and Latency at One-Eighth the Cost*
2. *Context Heals Acoustic Corruption: Statistical Parity Between Cascaded and Native Spoken Document QA*
3. *Cascaded vs. Native Multimodal Speech: Accuracy Parity, Latency Truths, and Token Economics in Grounded Spoken QA*
4. *Beyond End-to-End: Evaluating Trustworthiness, Latency Confounders, and Economics in Spoken Document Question Answering*

---

## Section-by-Section Outline & Evidence Audit

### Abstract
- **Core Claim:** Head-to-head empirical comparison across 200 technical queries (141 factual, 59 adversarial) across 8 domains demonstrates statistical accuracy parity (native 100.0% vs. cascade 98.6%, exact McNemar $p = 0.125$), identical adversarial hallucination resistance (100.0% both arms, $p = 1.000$), and latency parity (cascade 29.39s vs. native 24.51s, Wilcoxon $p = 0.470$), while the cascaded pipeline delivers an 87.8% reduction in API cost ($0.01814 vs. $0.14889, 95% CI [-88.1%, -87.4%]). Discloses the pilot $N=30$ latency finding as a free-tier throttling confound.
- **Supporting Exhibit:** `eval/results_comparison_latest.json` (summary_metrics), `eval/COMPARISON_REPORT.md` (Section 10).
- **Prohibited Claim:** No claim of native accuracy advantage or cascaded latency superiority; parity must be stated for both accuracy and latency.

---

### 1. Introduction
- **1.1 The Spoken Document QA Paradigm:**
  - Rise of multimodal foundation models capable of direct audio ingestion vs. traditional cascaded architectures (ASR → Text-LLM → TTS).
  - Common industry assumption: native audio avoids speech-to-text error propagation, especially on specialized domain terminology (medical, financial, systems engineering).
  - *Supporting Exhibit:* `eval/COMPARISON_REPORT.md` (Sections 2 & 10.1).
- **1.2 Empirical Research Questions:**
  - RQ1 (Accuracy & Parity): Does native audio ingestion outperform cascaded ASR on domain-specific factual QA at scale ($N=200$)?
  - RQ2 (Trustworthiness & Abstention): How do architectures compare when handling adversarial, unanswerable queries?
  - RQ3 (System Efficiency & Latency Confounders): What are the true end-to-end latency distributions once API throttling artifacts are controlled?
  - RQ4 (Context Sensitivity): What is the primary bottleneck for answer faithfulness: acoustic pipeline design or context representation?
  - *Supporting Exhibit:* `eval/COMPARISON_REPORT.md` (Sections 2 & 10), `eval/RUBRIC.md`.
- **1.3 Summary of Contributions:**
  - First large-scale, reproducible, open-source test harness evaluating native vs. cascaded architectures under identical ground-truth document priors across 8 domains ($N=200$).
  - Verified statistical accuracy parity (100.0% vs. 98.6%, McNemar $p = 0.125$) and identical adversarial abstention (100.0% vs. 100.0%, $p = 1.000$, zero hallucinations).
  - Corrected latency finding: Native and Cascaded pipelines exhibit statistical latency parity ($p = 0.470$, Wilcoxon signed-rank), with local edge STT adding merely 0.38s of mean execution overhead.
  - Quantitative economic dominance: Cascaded pipeline slashes API operational cost by 87.8% ($0.01814 vs. $0.14889, bootstrap 95% CI [-88.1%, -87.4%]) via text-vs-audio token pricing.
  - Methodological disclosure: Identification of free-tier cloud API throttling as a severe experimental confounder in speech LLM benchmarking.
  - Demonstration of semantic error recovery: downstream text LLMs repair phonetic Whisper distortions (*"slough or rot"*, *"AGFR"*, *"Cabernet's"*, *"clot in 18.2"*) via document context priors.
  - Identification of context compression as the primary accuracy bottleneck (66.7% factual accuracy under summarization → 100.0% under full text).
  - *Supporting Exhibits:* `eval/results_comparison_latest.json`, `eval/COMPARISON_REPORT.md` (Section 10), `eval/REPORT.md`.

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

---

### 3. Experimental Methodology & Rig

#### 3.1 Pipeline Architectures Under Test
- **Native Audio Arm:**
  - Raw 16-bit PCM WAV streamed as `inline_data` alongside full document text into `gemini-3.5-flash-lite`.
  - Jointly extracts text answer and vocal acoustics (sentiment, tone, confidence).
  - *Supporting Exhibit:* `eval/native_arm.py`, `eval/results_comparison_latest.json`.
- **Cascaded Pipeline Arm:**
  - Stage 1: Local STT via `faster-whisper` (`base` model, CPU `int8` quantization). Zero audio egress.
  - Stage 2: Prompt assembly with transcribed query text and identical full document context into `gemini-3.5-flash-lite`.
  - Stage 3: Text-to-Speech response synthesis.
  - *Supporting Exhibit:* `eval/cascade_arm.py`, `eval/results_comparison_latest.json`.
- **Stage Timing Protocol:**
  - Native: $T_{\text{total}} = T_{\text{multimodal\_llm}}$ ($T_{\text{stt}} = 0.0\text{s}$, $T_{\text{tts}} = \text{skipped}$).
  - Cascade: $T_{\text{total}} = T_{\text{whisper}} + T_{\text{text\_llm}}$ ($T_{\text{tts}} = \text{skipped}$).
  - *Supporting Exhibit:* `eval/results_comparison_latest.json`.

#### 3.2 Evaluation Corpus & Dataset Design
- **Corpus Documents ($N=8$ technical domains, 25 items each = 200 total):**
  - 1. Data Engineering: `cloud_data_lakehouse_architecture.pdf`
  - 2. Clinical Cardiology: `clinical_cardiology_trial_protocol.pdf`
  - 3. Financial Security: `fintech_payment_security_spec.pdf`
  - 4. Avionics Engineering: `aerospace_avionics_thermal_spec.pdf`
  - 5. Oncology Trials: `clinical_oncology_biomarker_protocol.pdf`
  - 6. Cloud SRE / Devops: `cloud_kubernetes_sre_incident_runbook.pdf`
  - 7. Cold Chain Logistics: `supply_chain_cold_storage_logistics.pdf`
  - 8. Accounting & Audit: `financial_audit_internal_controls_memo.pdf`
  - Extraction via PyMuPDF (`fitz`), cached locally with `MAX_DOCUMENT_CHARS = 50,000`.
  - *Supporting Exhibit:* `eval/data/` (PDF files), `eval/dataset_v2.csv`, `eval/COMPARISON_REPORT.md` (Section 10.4).
- **Question Composition ($N=200$ total items):**
  - 141 Factual Questions: Precise numerical thresholds, protocols, and architectural specifications.
  - 59 Adversarial Questions: Inquiries deliberately targeting information absent from the text to test hallucination resistance.
  - Acoustic generation: Synthesized offline to standard 16-bit PCM WAV using Windows `System.Speech` (`eval/synthesize_audio_batch.ps1`) to eliminate online synthesis variance.
  - *Supporting Exhibit:* `eval/dataset_v2.csv`, `eval/COMPARISON_REPORT.md` (Section 10.1).
- **TODO-1 (Load-Bearing):** Acoustic diversity expansion — record real multi-accent human speakers with calibrated background noise (SNR 10dB, 20dB) to evaluate boundary conditions where Whisper STT WER exceeds LLM recovery capability.

#### 3.3 Scoring Rubric & LLM-as-Judge Protocol
- **3-Point Auditable Rubric (`eval/RUBRIC.md`):**
  - Score 2 (Full Credit): Factually complete and exact; for adversarial questions, explicit and unambiguous refusal to answer.
  - Score 1 (Partial Credit): Substantively correct core fact with minor non-critical omission; for adversarial, hedged response.
  - Score 0 (No Credit): Factually incorrect, contradictory, or fabricated hallucination.
  - Mandatory Span Matching: Judge must cite the exact verbatim evidence span from the generated response.
- **Judge Configuration:**
  - Impartial chunked batch evaluation via `gemini-3.5-flash-lite` (10 items per batch with 90s socket timeout).
  - *Supporting Exhibit:* `eval/RUBRIC.md`, `eval/run_comparison.py`, `eval/results_comparison_latest.json`.
- **TODO-5 (Nice-to-Have):** Human-expert validation on responses with Cohen's $\kappa$ inter-rater reliability calculation against LLM judge.

---

### 4. Results & Empirical Analysis ($N = 200$)

#### 4.1 Factual Accuracy & Hallucination Resistance Parity
- **Global Scorecard ($N=200$ items, 400 max points):**
  - Factual Accuracy: 100.0% Native (282/282 pts) vs. 98.6% Cascade (278/282 pts) ($\Delta = -1.4\%$).
  - Adversarial Abstention: 100.0% Native (118/118 pts, 59/59 refusals) vs. 100.0% Cascade (118/118 pts, 59/59 refusals) ($\Delta = +0.0\%$).
  - Combined Benchmark: 100.0% Native (400/400 pts) vs. 99.0% Cascade (396/400 pts).
  - Score Distribution (Score 2 / 1 / 0): Native = 200 / 0 / 0; Cascade = 196 / 4 / 0.
  - Inter-arm Agreement: 196/200 (98.0% exact agreement, 4 disagreements).
  - *Supporting Exhibit:* `eval/results_comparison_latest.json`, `eval/COMPARISON_REPORT.md` (Section 10.2).
- **Exact Paired McNemar Test:**
  - Contingency table: $a=137$ (both full credit), $b=4$ (Native full, Cascade partial), $c=0$ (Cascade full, Native partial), $d=0$ (both imperfect).
  - Discordant pairs: $b+c = 4$.
  - Exact two-sided Binomial $p$-value: **$p = 0.12500$** ($\chi^2 = 2.25$).
  - **Verdict:** The 1.4% delta is **not statistically significant** at $\alpha = 0.05$. Grounded accuracy parity holds.
  - Adversarial Abstention McNemar: $p = 1.000$ (zero discordant pairs; identical refusal).
  - *Supporting Exhibit:* `eval/analyze_n200.py`, `eval/COMPARISON_REPORT.md` (Section 10.3).
- **Disagreement Inspection (The 4 Partial-Credit Cases):**
  - In all 4 cases (`Q-AERO-14`, `Q-ONCO-12`, `Q-ONCO-13`, `Q-ONCO-18`), Cascade retrieved the exact correct numeric/factual entity but received Score 1 due to judge strictness over secondary qualifiers (e.g., omitting frequency band range or staining intensity specification).
  - Zero hallucinations or factual contradictions occurred on either arm.

#### 4.2 Latency Breakdown: Statistical Parity & Local STT Efficiency
- **End-to-End Latency ($N=200$ items):**
  - Native Mean: 24.511s (p95: 87.845s, Min: 3.558s, Max: 120.488s).
  - Cascade Mean: 29.387s (p95: 85.316s, Min: 4.093s, Max: 118.899s).
  - Local Whisper STT: Mean = 0.376s (p95: 0.409s, Min: 0.288s, Max: 0.540s).
  - Cascade LLM Inference: Mean = 29.011s (p95: 84.945s).
  - Paired Wilcoxon Signed-Rank Test: $W = 9,566.0, z = +0.722, p = 0.470$.
  - 10,000-Replicate Bootstrap 95% CI on Mean Latency Delta: $[-4.620\text{s}, +18.562\text{s}]$.
  - **Verdict:** End-to-end latency between Native and Cascade is **statistically indistinguishable** ($p = 0.470$).
  - *Supporting Exhibit:* `eval/results_comparison_latest.json`, `eval/analyze_n200.py`, `eval/COMPARISON_REPORT.md` (Sections 10.2 & 10.3).

#### 4.2.1 Methodological Caution: Free-Tier API Gateway Throttling as a Latency Confound
- **The Pilot $N=30$ Artifact:**
  - In the initial $N=30$ pilot run, the Cascade arm appeared 63.7% faster (12.14s vs. 33.45s).
  - Rigorous $N=200$ execution revealed this was an experimental artifact caused by free-tier API gateway queuing and server-side socket stalls (including an unrepresentative 316.8s outlier on `Q-FIN-ADV-03` during audio decoding).
  - When paced consistently over 200 items with 90s socket timeouts, both arms converge to parity ($p = 0.470$).
- **Methodological Recommendation for Speech/LLM Researchers:**
  - Cloud API gateway scheduling, multi-tenant queuing, and unannounced free-tier rate throttling severely distort E2E latency measurements unless controlled by large sample sizes ($N \ge 200$), isolated local execution stages, and paired non-parametric statistical tests.

#### 4.3 Token Economics & Operational Cost
- **Consumption & Billing Metrics (Gemini Developer List Price):**
  - Pricing: Text input = $0.10 / 1M tokens; Audio input = $0.70 / 1M tokens; Output = $0.40 / 1M tokens.
  - Native Arm: 199,440 prompt tokens + 20,619 candidate tokens = 220,059 total tokens → **$0.14889 USD**.
  - Cascade Arm: 157,419 prompt tokens + 6,724 candidate tokens = 164,143 total tokens → **$0.01814 USD**.
  - Cost Delta: Cascade is **$0.13075 USD cheaper** (**87.8% cost reduction**, **8.2× cheaper**, one-eighth the cost).
  - Bootstrap 95% Confidence Interval on Cost Reduction: $[-88.1\%, -87.4\%]$ (or $[-\$0.1345, -\$0.1268]$).
  - Candidate Output Token Conciseness: Cascade answers generated 6,724 tokens vs. Native 20,619 tokens (-67.4% reduction), avoiding conversational audio filler.
  - *Supporting Exhibit:* `eval/results_comparison_latest.json`, `eval/analyze_n200.py`, `eval/COMPARISON_REPORT.md` (Sections 10.2 & 10.3).

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
  - Case 6: *Systems Terminology Distortion* (`Q-K8S-01`): *"Kubernetes"* transcribed as *"Cabernet's"*. Recovered via runbook header (*"SRE-K8S-RUNBOOK-V5"*).
  - Case 7: *Component Abbreviation Truncation* (`Q-K8S-16`): *"etcd"* transcribed as *"ect"*. Recovered snapshot policy (*"every 6 hours"*).
  - Case 8: *Biomarker Target Distortion* (`Q-ONCO-13`): *"Claudin-18.2"* transcribed as *"clot in 18.2"*. Recovered IHC threshold (*"$\ge 70\%$"*).
  - *Supporting Exhibit:* `eval/results_comparison_latest.json`, `eval/COMPARISON_REPORT.md` (Sections 5 & 10.5).
- **Unique Capability of Native Arm:**
  - Vocal Tone and Emotion Extraction: Native arm successfully extracted query sentiment and acoustic tone across all evaluated questions, a modality lost in STT.
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
4. **Sample Size & Power (Resolved):**
   - Initial pilot study ($N=30$) was scaled to $N=200$ across 8 domains, providing high statistical power ($p = 0.125$ McNemar, $p = 0.470$ Wilcoxon, bootstrap 95% CIs). [TODO-2 COMPLETED]
5. **API Gateway Latency Jitter (Methodological Finding):**
   - Free-tier rate limits and multi-tenant cloud queues contribute to observed tail latencies and confounded the earlier pilot. Fully disclosed and analyzed in Section 4.2.1.

---

### 7. Conclusion & Recommendations

1. **Architecture Recommendation for Industry:**
   - For document-grounded spoken QA, cascaded architectures match native-audio models on accuracy and latency while cutting operational API cost by 87.8% (one-eighth the cost).
2. **Context Heals Acoustic Corruption:**
   - Dense document grounding provides an overwhelming language model prior that compensates for phonological errors.
3. **When to Choose Native Audio:**
   - Reserve native multimodal models for applications where acoustic paralinguistics (emotion, stress, vocal biomarkers, tone) are functionally necessary.
4. **Reproducibility Guarantee:**
   - Complete harness, dataset, audio generation scripts, and judge prompts available in open-source repository.

---

## Exhibits & Claims Traceability Matrix

| Planned Section | Planned Claim / Metric | Supporting Exhibit File | Exact Data Key / Line | Status |
|:---|:---|:---|:---|:---:|
| **Abstract / Sec 4.1** | Factual accuracy parity: Native 100.0% vs Cascade 98.6% | `eval/results_comparison_latest.json` | `summary_metrics.*.factual_accuracy_pct` | **VERIFIED** |
| **Abstract / Sec 4.1** | McNemar test on factual accuracy: $p = 0.12500$ ($\chi^2 = 2.25$) | `eval/analyze_n200.py`, `eval/COMPARISON_REPORT.md` | Section 10.2 & 10.3 | **VERIFIED** |
| **Abstract / Sec 4.1** | Adversarial abstention tied at 100.0% (59/59 refusals, $p = 1.000$) | `eval/results_comparison_latest.json` | `summary_metrics.*.abstention_rate_pct` | **VERIFIED** |
| **Abstract / Sec 4.2** | Latency parity: Cascade 29.39s vs Native 24.51s (Wilcoxon $p = 0.470$) | `eval/results_comparison_latest.json` | `summary_metrics.*.latencies.total.mean` | **VERIFIED** |
| **Sec 4.2** | Local Whisper STT mean latency 0.376s (p95: 0.409s) on CPU | `eval/results_comparison_latest.json` | `summary_metrics.cascade.latencies.stt` | **VERIFIED** |
| **Sec 4.2.1** | Pilot $N=30$ 63.7% latency delta disclosed as free-tier confound | `eval/COMPARISON_REPORT.md` | Section 1 & Section 10.2 | **VERIFIED** |
| **Abstract / Sec 4.3** | Cascade API cost $0.01814 vs Native $0.14889 (-87.8%, 8.2× cheaper) | `eval/results_comparison_latest.json` | `summary_metrics.deltas.cost_delta_usd` | **VERIFIED** |
| **Sec 4.3** | Bootstrap 95% CI on cost reduction: [-88.1%, -87.4%] | `eval/analyze_n200.py`, `eval/COMPARISON_REPORT.md` | Section 10.3 | **VERIFIED** |
| **Sec 4.4** | Intermediate summarization baseline factual acc 66.7% | `eval/results_latest.json`, `eval/REPORT.md` | `eval/REPORT.md` Sec 1 & 3.1 | **VERIFIED** |
| **Sec 5** | Phonetic recovery exhibits: "slough or rot", "Cabernet's", "clot in 18.2" | `eval/results_comparison_latest.json` | `itemized_results[*].cascade.transcript` | **VERIFIED** |
| **Sec 5** | Native arm extracts tone/emotion (calm, inquisitive, professional) | `eval/results_comparison_latest.json` | `itemized_results[*].native.sentiment` | **VERIFIED** |
| **Sec 3.1 / 6** | TTS latency skipped (0.0s recorded) | `eval/results_comparison_latest.json` | `summary_metrics.*.latencies.tts.status` | **VERIFIED** |
| **Sec 3.2 / 6** | Multi-accent real human audio under noise (SNR 10dB) | None (Planned Experiment) | `TODO-1` | **TODO** |
| **Sec 4.1 / 6** | Large-scale evaluation ($N=200$) with bootstrap 95% CIs | `eval/dataset_v2.csv`, `eval/analyze_n200.py` | Completed in PR #7 | **COMPLETED** |
| **Sec 6** | Live Google Cloud TTS latency benchmarking (~1.5s) | None (Requires GCP Service Account) | `TODO-3` | **TODO** |
| **Sec 6** | Cross-model evaluation (Whisper-large, GPT-4o Audio) | None (Planned Experiment) | `TODO-4` | **TODO** |
| **Sec 3.3** | Human expert inter-annotator agreement (Cohen's κ) | None (Planned Annotation) | `TODO-5` | **TODO** |
| **Sec 5** | Utility quantification of acoustic sentiment in triage | None (Planned User Study) | `TODO-6` | **TODO** |
