# Figures & Tables Plan: Interspeech 2027 Workshop Paper

Every table and figure planned for the paper is mapped directly to measured repository exhibits in `eval/results_comparison_latest.json`, `eval/results_latest.json`, `eval/REPORT.md`, and `eval/COMPARISON_REPORT.md`.

---

## 1. Table 1: Task Accuracy, Adversarial Abstention, and Parity Scorecard

**Caption:** *Task performance on domain-specific spoken document question answering across 30 questions (21 factual, 9 unanswerable adversarial) evaluated under full document context.*

| Table Column | Native Audio Arm | Cascaded Arm | Delta ($\Delta$) | Data Source Key in `eval/results_comparison_latest.json` |
|:---|:---:|:---:|:---:|:---|
| **Factual Accuracy Rate** | 100.0% (42/42 pts) | 100.0% (42/42 pts) | 0.0% (Tie) | `summary_metrics.native.factual_accuracy_pct` vs `summary_metrics.cascade.factual_accuracy_pct` |
| **Factual Full Credit (Score 2)** | 21 / 21 items | 21 / 21 items | 0 | `summary_metrics.native.score_counts.score_2` (factual subset) |
| **Factual Partial Credit (Score 1)** | 0 / 21 items | 0 / 21 items | 0 | `summary_metrics.native.score_counts.score_1` |
| **Factual Missed (Score 0)** | 0 / 21 items | 0 / 21 items | 0 | `summary_metrics.native.score_counts.score_0` |
| **Hallucination Resistance** | 100.0% (18/18 pts) | 100.0% (18/18 pts) | 0.0% (Tie) | `summary_metrics.native.hallucination_resistance_pct` vs `summary_metrics.cascade.hallucination_resistance_pct` |
| **Adversarial Abstention Rate** | 100.0% (9/9 items) | 100.0% (9/9 items) | 0.0% (Tie) | `summary_metrics.native.abstention_rate_pct` vs `summary_metrics.cascade.abstention_rate_pct` |
| **Combined Benchmark Accuracy** | 100.0% (60/60 pts) | 100.0% (60/60 pts) | 0.0% (Tie) | `summary_metrics.native.overall_benchmark_pct` vs `summary_metrics.cascade.overall_benchmark_pct` |
| **Inter-Arm Agreement Rate** | 100.0% (30/30) | 100.0% (30/30) | 0.0% | `itemized_results[*].arms_agree` |

---

## 2. Table 2: Per-Stage Latency Breakdown & Distribution Statistics

**Caption:** *Per-stage and end-to-end response latency statistics (seconds) across 30 spoken queries on commodity CPU (`faster-whisper-base` int8) and cloud Gemini 3.1 Flash-Lite.*

| Stage | Metric | Native Arm | Cascade Arm | Delta (Cascade − Native) | Percent Change | Data Source Key in `eval/results_comparison_latest.json` |
|:---|:---|:---:|:---:|:---:|:---:|:---|
| **Speech-to-Text (STT)** | Mean | 0.000s | **0.409s** | +0.409s | N/A | `summary_metrics.cascade.latencies.stt.mean` |
| | p95 | 0.000s | **0.582s** | +0.582s | N/A | `summary_metrics.cascade.latencies.stt.p95` |
| | Min / Max | 0.0s / 0.0s | 0.331s / 0.650s | +0.331s / +0.650s | N/A | `summary_metrics.cascade.latencies.stt.min`, `max` |
| **LLM Inference (Doc QA)** | Mean | 33.450s | **11.727s** | −21.723s | −64.9% | `summary_metrics.native.latencies.llm.mean` vs `cascade...llm.mean` |
| | p95 | 71.633s | **24.606s** | −47.027s | −65.6% | `summary_metrics.native.latencies.llm.p95` vs `cascade...llm.p95` |
| | Min / Max | 5.127s / 316.762s | 3.037s / 61.493s | −2.090s / −255.269s | — | `summary_metrics.native.latencies.llm.min`, `max` |
| **Text-to-Speech (TTS)** | Status | *SKIPPED* | *SKIPPED* | 0.000s | 0.0% | `summary_metrics.*.latencies.tts.status` |
| **Total End-to-End** | **Mean** | **33.450s** | **12.136s** | **−21.314s** | **−63.7%** | `summary_metrics.deltas.mean_latency_delta_sec` |
| | **p95** | **71.633s** | **24.969s** | **−46.664s** | **−65.1%** | Computed from `summary_metrics.*.latencies.total.p95` |
| | **Min** | 5.127s | 3.382s | −1.745s | −34.0% | `summary_metrics.*.latencies.total.min` |
| | **Max** | 316.762s | 61.836s | −254.926s | −80.5% | `summary_metrics.*.latencies.total.max` |

---

## 3. Table 3: Token Economics & Operational API Cost Comparison

**Caption:** *Token consumption and estimated API operational cost across 30 spoken queries using Gemini 3.1 Flash-Lite developer list pricing.*

| Metric | Native Audio Arm | Cascaded Arm | Delta (Cascade − Native) | Percent Change | Data Source Key in `eval/results_comparison_latest.json` |
|:---|:---:|:---:|:---:|:---:|:---|
| **Input Token Unit Price** | $0.70 / 1M (audio) | $0.10 / 1M (text) | −$0.60 / 1M | −85.7% | `eval/run_comparison.py`, `PRICING_PER_1M_TOKENS` |
| **Output Token Unit Price** | $0.40 / 1M (text) | $0.40 / 1M (text) | $0.00 | 0.0% | `eval/run_comparison.py`, `PRICING_PER_1M_TOKENS` |
| **Total Prompt Tokens** | 26,907 | 20,448 | −6,459 | −24.0% | `summary_metrics.native.tokens.prompt_tokens` vs `cascade` |
| **Total Candidate Output Tokens** | 2,520 | 873 | −1,647 | −65.4% | `summary_metrics.native.tokens.candidates_tokens` vs `cascade` |
| **Total Tokens Consumed** | **29,427** | **21,321** | **−8,106** | **−27.5%** | `summary_metrics.native.tokens.total_tokens` vs `cascade` |
| **Theoretical API Cost (USD)** | **$0.01984** | **$0.00239** | **−$0.01745** | **−88.0%** | `summary_metrics.deltas.cost_delta_usd` |
| **Cost Reduction Multiplier** | 1.0× (Baseline) | **8.3× Cheaper** | +7.3× | — | Computed from cost ratio: 0.01984 / 0.00239 |
| **Actual Billed Cost (Free Tier)** | $0.00 | $0.00 | $0.00 | 0.0% | `summary_metrics.*.actual_charged_cost_usd` |

---

## 4. Table 4: Phonetic Distortion vs. Semantic Context Recovery Case Studies

**Caption:** *Representative case studies from the 30-item evaluation showing acoustic transcription distortions introduced by local Whisper and resolved by document context.*

| Item ID | Domain | Ground Truth Spoken Query | Whisper STT Transcript | Final Cascade Answer | Linguistic Distortion Category | Document Context Recovery Mechanism | Exhibit Line in `eval/results_comparison_latest.json` |
|:---|:---|:---|:---|:---|:---|:---|:---|
| `Q-DLH-01` | Data Eng | *"What table format is used for all transformed tables in the Gold analytical layer?"* | *"What table format is used?"* | *"All transformed tables in the Gold analytical layer are formatted as Apache Iceberg v2 tables."* | **Clause Truncation** | Document table format specification for Gold tier resolves omitted clause. | Lines 178–233 |
| `Q-DLH-02` | Data Eng | *"What is the sustained ingestion SLA for raw transactional events captured from Kafka topics?"* | *"What is the sustained ingestion slough or rot transactional events captured from Kafka topics?"* | *"The sustained ingestion SLA for raw transactional events captured from Kafka topics is under 500 milliseconds (p95)."* | **Phonetic Confusion** (*"SLA for raw"* → *"slough or rot"*) | Kafka ingestion section and 500ms p95 metric provide unambiguous prior. | Lines 238–293 |
| `Q-DLH-05` | Data Eng | *"How long are aggregated financial marts retained for regulatory compliance?"* | *"How long are aggregated financial marks retained for regulatory compliance?"* | *"Aggregated financial marts are retained for 7 years for regulatory compliance."* | **Homophone Substitution** (*"marts"* → *"marks"*) | Regulatory compliance retention policy table grounds duration to 7 years. | Lines 418–473 |
| `Q-CLIN-04` | Cardiology | *"What is the baseline estimated Glomerular Filtration Rate (eGFR) below which subjects are excluded?"* | *"What is the baseline estimated glomerular filtration rate, AGFR, below which subjects are excluded?"* | *"Subjects are excluded if their baseline eGFR is below 30 mL/min/1.73 m²."* | **Acronym Misrecognition** (*"eGFR"* → *"AGFR"*) | Spoken expanded form disambiguates acronym error; exclusion threshold matched. | Lines 958–1013 |
| `Q-CLIN-06` | Cardiology | *"What threshold of Grade 3 hypotension triggers the predefined study halting criteria?"* | *"What threshold of grade 3 hypertension triggers the predefined study halting criteria?"* | *"Predefined study halting criteria are triggered if Grade 3 hypotension exceeds 2.5% in any active treatment arm."* | **Semantic Inversion** (*"hypotension"* → *"hypertension"*) | Halting criteria table in protocol only defines threshold for hypotension (2.5%). | Lines 1078–1133 |
| `Q-CLIN-ADV-01` | Cardiology | *"What is the recommended pediatric dosage for Cardiovastin in children under 12 years old?"* | *"What is the recommended pediatric dosage for cardioveston in children under 12 years old?"* | *Explicit refusal: Protocol restricts enrollment to adults aged 35–75; no pediatric dosage exists.* | **Proper Noun Distortion** (*"Cardiovastin"* → *"cardioveston"*) | Trial protocol inclusion criteria state adults only; model abstains identically to Native. | Lines 1138–1193 |
| `Q-FIN-07` | Fintech | *"What is the financial settlement SLA for issuing banks to complete dispute arbitration?"* | *"What is the financial settlements law for issuing banks to complete dispute arbitration?"* | *"Within 45 calendar days."* | **Phonetic Merger** (*"settlement SLA"* → *"settlements law"*) | Dispute arbitration section defines 45-day SLA; legal phrasing mapped to SLA table. | Lines 1608–1663 |
| `Q-FIN-ADV-03` | Fintech | *"What cryptocurrency assets are accepted for settlement on the payment switch?"* | *"What cryptocurrency assets are accepted for settlement on the payment switch?"* | *Explicit refusal: Payment switch specification mentions no cryptocurrency assets.* | **Tail Latency Anomaly** (Cascade: 6.72s vs Native: 316.76s) | Clean STT; Native arm suffered 316.8s multimodal server decoding delay before abstaining. | Lines 1828–1883 |

---

## 5. Table 5: Architectural Ablation: Context Compression vs. Full Grounding

**Caption:** *Comparative accuracy and latency between intermediate document summarization (`summarize_book`) and full document context injection (`MAX_DOCUMENT_CHARS = 50,000`).*

| Pipeline Configuration | Context Injection Method | Evaluation Set Size | Factual Accuracy | Hallucination Resistance | Combined Benchmark | Mean Audio Inference Latency | Data Source Exhibit |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---|
| **Compressed Context (Baseline)** | Intermediate Gemini Summary (~500 words) | $N=12$ items (9 fact, 3 adv) | **66.7%** (12/18 pts) | **100.0%** (6/6 pts) | **75.0%** (18/24 pts) | 27.179s (p95: 110.454s) | `eval/results_latest.json`, `eval/REPORT.md` |
| **Full Document Context (Refactored)** | Complete Extracted PDF Text ($\le$50k chars) | $N=30$ items (21 fact, 9 adv) | **100.0%** (42/42 pts) | **100.0%** (18/18 pts) | **100.0%** (60/60 pts) | 33.450s (Native) / 12.136s (Cascade) | `eval/results_comparison_latest.json` |

---

## 6. Figure 1: Architectural Comparison Flowchart

**Caption:** *System diagram comparing the Native-Audio Multimodal pipeline (top) with the Cascaded STT→LLM pipeline (bottom) for document-grounded spoken QA.*

- **Type:** TikZ / Mermaid vector architecture diagram.
- **Top Lane (Native Arm):** Spoken WAV Audio $\to$ Inline Audio Base64 Streaming $\to$ Google Gemini 3.1 Flash-Lite (Audio + Document Text) $\to$ Multimodal Parser $\to$ [Answer Text + Extracted Vocal Tone].
- **Bottom Lane (Cascade Arm):** Spoken WAV Audio $\to$ Local `faster-whisper-base` (CPU int8) $\to$ Transcribed Text Query $\to$ Google Gemini 3.1 Flash-Lite (Text Only + Document Text) $\to$ Text Parser $\to$ [Answer Text].
- **Data Source Reference:** `eval/COMPARISON_REPORT.md` Section 3.1; `eval/native_arm.py`; `eval/cascade_arm.py`.

---

## 7. Figure 2: End-to-End Latency Distribution and Tail Boxplot

**Caption:** *Empirical latency distributions (seconds) across all 30 queries, illustrating local STT predictability and severe multimodal server-side tail latency.*

- **Type:** Grouped Boxplot + Jittered Scatter or empirical Cumulative Distribution Function (eCDF).
- **Traces:**
  1. Cascade Total Latency (Median $\approx 10.5\text{s}$, p95: $24.97\text{s}$, Max: $61.84\text{s}$).
  2. Cascade STT Latency (Tight band: Mean $0.409\text{s}$, Max $0.650\text{s}$).
  3. Native Total Latency (Median $\approx 15.2\text{s}$, p95: $71.63\text{s}$, Outlier: $316.76\text{s}$).
- **Data Source Reference:** Raw timing values in `eval/results_comparison_latest.json` (`itemized_results[*].native.stage_latencies` and `itemized_results[*].cascade.stage_latencies`).

---

## 8. Figure 3: Cost vs. Latency Pareto Frontier

**Caption:** *Cost-latency trade-off space for document-grounded spoken QA. The cascaded pipeline strictly dominates native audio.*

- **Type:** 2D Scatter Plot.
  - X-Axis: Mean End-to-End Latency (seconds) — lower is better.
  - Y-Axis: API Cost per Query (USD) — lower is better.
- **Data Points:**
  - Native Audio: $(33.45\text{s}, \$0.000661/\text{query})$.
  - Cascaded Pipeline: $(12.14\text{s}, \$0.000080/\text{query})$.
- **Visual Callout:** Cascaded pipeline sits at the ideal bottom-left quadrant (2.76× faster, 8.3× cheaper) with zero accuracy degradation.
- **Data Source Reference:** `eval/results_comparison_latest.json` summary metrics.
