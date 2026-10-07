# Figures & Tables Plan: Interspeech 2027 Workshop Paper

Every table and figure planned for the paper is mapped directly to measured repository exhibits in `eval/results_comparison_latest.json`, `eval/analyze_n200.py`, `eval/REPORT.md`, and `eval/COMPARISON_REPORT.md` (Section 10).

---

## 1. Table 1: Task Accuracy, Adversarial Abstention, and Parity Scorecard ($N = 200$)

**Caption:** *Task performance on domain-specific spoken document question answering across 200 questions (141 factual, 59 unanswerable adversarial) across 8 technical domains evaluated under full document context.*

| Table Column | Native Audio Arm | Cascaded Arm | Delta ($\Delta$) | Statistical Significance ($p$-value) | Data Source Key in `eval/results_comparison_latest.json` |
|:---|:---:|:---:|:---:|:---:|:---|
| **Factual Accuracy Rate** | 100.0% (282/282 pts) | 98.6% (278/282 pts) | −1.4% | $p = 0.12500$ (McNemar, not significant) | `summary_metrics.native.factual_accuracy_pct` vs `cascade` |
| **Factual Full Credit (Score 2)** | 141 / 141 items | 137 / 141 items | −4 items | N/A | `summary_metrics.native.score_counts.score_2` |
| **Factual Partial Credit (Score 1)** | 0 / 141 items | 4 / 141 items | +4 items | N/A (Judge strictness on secondary qualifiers) | `summary_metrics.cascade.score_counts.score_1` |
| **Factual Missed (Score 0)** | 0 / 141 items | 0 / 141 items | 0 (Tie) | N/A (Zero factual failures) | `summary_metrics.*.score_counts.score_0` |
| **Hallucination Resistance** | 100.0% (118/118 pts) | 100.0% (118/118 pts) | 0.0% (Tie) | $p = 1.00000$ (Exact McNemar, 0 discordant) | `summary_metrics.*.hallucination_resistance_pct` |
| **Adversarial Abstention Rate** | 100.0% (59/59 items) | 100.0% (59/59 items) | 0.0% (Tie) | $p = 1.00000$ (Zero hallucinations) | `summary_metrics.*.abstention_rate_pct` |
| **Combined Benchmark Accuracy** | 100.0% (400/400 pts) | 99.0% (396/400 pts) | −1.0% | $p = 0.12500$ (Accuracy parity holds) | `summary_metrics.*.overall_benchmark_pct` |
| **Inter-Arm Agreement Rate** | 100.0% (Baseline) | 98.0% (196/200) | −2.0% | 4 partial-credit disagreements, 0 contradictions | `itemized_results[*].arms_agree` |

---

## 2. Table 2: Per-Stage Latency Breakdown & Distribution Statistics ($N = 200$)

**Caption:** *Per-stage and end-to-end response latency statistics (seconds) across 200 spoken queries on commodity CPU (`faster-whisper-base` int8) and cloud Gemini 3.5 Flash-Lite, alongside historical pilot comparison showing API throttling artifacts.*

| Evaluation Run | Stage | Metric | Native Arm | Cascade Arm | Delta (Cascade − Native) | Percent Change | Data Source Key / Note |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---|
| **Canonical $N=200$ Run** | **Speech-to-Text (STT)** | Mean | 0.000s | **0.376s** | +0.376s | N/A | `summary_metrics.cascade.latencies.stt.mean` |
| | | p95 | 0.000s | **0.409s** | +0.409s | N/A | `summary_metrics.cascade.latencies.stt.p95` |
| | | Min / Max | 0.0s / 0.0s | 0.288s / 0.540s | +0.288s / +0.540s | N/A | `summary_metrics.cascade.latencies.stt.min`, `max` |
| | **LLM Inference (Doc QA)** | Mean | 24.511s | 29.011s | +4.500s | +18.4% | `summary_metrics.native.latencies.llm.mean` vs `cascade` |
| | | p95 | 87.845s | 84.945s | −2.900s | −3.3% | `summary_metrics.native.latencies.llm.p95` vs `cascade` |
| | | Min / Max | 3.558s / 120.488s | 3.753s / 118.523s | +0.195s / −1.965s | — | `summary_metrics.*.latencies.llm.min`, `max` |
| | **Text-to-Speech (TTS)** | Status | *SKIPPED* | *SKIPPED* | 0.000s | 0.0% | `summary_metrics.*.latencies.tts.status` |
| | **Total End-to-End** | **Mean** | **24.511s** | **29.387s** | **+4.876s** | **+19.9%** | **Wilcoxon $p = 0.470$ (Latency Parity)** |
| | | **p95** | **87.845s** | **85.316s** | **−2.529s** | **−2.9%** | Lower tail latency on Cascade at p95 |
| | | **Min** | 3.558s | 4.093s | +0.535s | +15.0% | `summary_metrics.*.latencies.total.min` |
| | | **Max** | 120.488s | 118.899s | −1.589s | −1.3% | `summary_metrics.*.latencies.total.max` |
| *Pilot ($N=30$, Free-Tier Confounded)* | *Total End-to-End* | *Mean* | *33.450s* | *12.136s* | *−21.314s* | *−63.7%* | *Confounded by API gateway queuing & 316.8s stall* |
| *Pilot ($N=30$, Free-Tier Confounded)* | *Total End-to-End* | *p95* | *71.633s* | *24.969s* | *−46.664s* | *−65.1%* | *Unrepresentative tail artifact from unthrottled burst* |

---

## 3. Table 3: Token Economics & Operational API Cost Comparison ($N = 200$)

**Caption:** *Token consumption and estimated API operational cost across 200 spoken queries using Gemini 3.5 Flash-Lite developer list pricing.*

| Metric | Native Audio Arm | Cascaded Arm | Delta (Cascade − Native) | Percent Change | Data Source Key in `eval/results_comparison_latest.json` |
|:---|:---:|:---:|:---:|:---:|:---|
| **Input Token Unit Price** | $0.70 / 1M (audio) | $0.10 / 1M (text) | −$0.60 / 1M | −85.7% | `eval/run_comparison.py`, `PRICING_PER_1M_TOKENS` |
| **Output Token Unit Price** | $0.40 / 1M (text) | $0.40 / 1M (text) | $0.00 | 0.0% | `eval/run_comparison.py`, `PRICING_PER_1M_TOKENS` |
| **Total Prompt Tokens** | 199,440 | 157,419 | −42,021 | −21.1% | `summary_metrics.native.tokens.prompt_tokens` vs `cascade` |
| **Total Candidate Output Tokens** | 20,619 | 6,724 | −13,895 | −67.4% | `summary_metrics.native.tokens.candidates_tokens` vs `cascade` |
| **Total Tokens Consumed** | **220,059** | **164,143** | **−55,916** | **−25.4%** | `summary_metrics.native.tokens.total_tokens` vs `cascade` |
| **Theoretical API Cost (USD)** | **$0.14889** | **$0.01814** | **−$0.13075** | **−87.8%** | `summary_metrics.deltas.cost_delta_usd` |
| **Bootstrap 95% CI on Cost Reduction** | — | — | **[−88.1%, −87.4%]** | — | `eval/analyze_n200.py`, Section 10.3 |
| **Cost Reduction Multiplier** | 1.0× (Baseline) | **8.2× Cheaper** | +7.2× | — | Computed: $0.14889 / $0.01814 (one-eighth the cost) |
| **Actual Billed Cost (Free Tier)** | $0.00 | $0.00 | $0.00 | 0.0% | `summary_metrics.*.actual_charged_cost_usd` |

---

## 4. Table 4: Phonetic Distortion vs. Semantic Context Recovery & Disagreement Exhibits

**Caption:** *Representative case studies from the 200-item evaluation illustrating acoustic transcription distortions resolved by document context, alongside the four partial-credit disagreement cases.*

| Item ID | Domain | Ground Truth Spoken Query | Whisper STT Transcript | Final Cascade Answer | Linguistic / Disagreement Category | Document Context Recovery Mechanism / Judge Scoring |
|:---|:---|:---|:---|:---|:---|:---|
| `Q-K8S-01` | Cloud SRE | *"What is the formal runbook title and document control identifier for Kubernetes incident response?"* | *"What is the formal runbook title and document control identifier for Cabernet's incident response?"* | *"SRE-K8S-RUNBOOK-V5"* | **Systems Terminology Distortion** (*"Kubernetes"* → *"Cabernet's"*) | Runbook title and document control section unambiguously grounds identifier. |
| `Q-K8S-16` | Cloud SRE | *"How frequently are automated etcd snapshots scheduled to run across the primary cluster?"* | *"How frequently are automated ect snapshots scheduled to run across the primary cluster?"* | *"Automated etcd snapshots are scheduled to run every 6 hours."* | **Component Truncation** (*"etcd"* → *"ect"*) | Control plane snapshot section explicitly defines 6-hour interval. |
| `Q-ONCO-13` | Oncology | *"What expression threshold of Claudin-18.2 in tumor cells is required for study eligibility?"* | *"What expression threshold of clot in 18.2 in tumor cells is required for study eligibility?"* | *"Greater than or equal to 70% of tumor cells."* | **Biomarker Name Distortion** (*"Claudin-18.2"* → *"clot in 18.2"*) | Inclusion criteria IHC table grounds target antigen and $\ge 70\%$ threshold. |
| `Q-DLH-02` | Data Eng | *"What is the sustained ingestion SLA for raw transactional events captured from Kafka topics?"* | *"What is the sustained ingestion slough or rot transactional events captured from Kafka topics?"* | *"Under 500 milliseconds (p95)."* | **Phonetic Confusion** (*"SLA for raw"* → *"slough or rot"*) | Kafka ingestion section grounds latency metric. |
| `Q-CLIN-04` | Cardiology | *"What is the baseline estimated Glomerular Filtration Rate (eGFR) below which subjects are excluded?"* | *"What is the baseline estimated glomerular filtration rate, AGFR, below which subjects are excluded?"* | *"Below 30 mL/min/1.73 m²."* | **Acronym Misrecognition** (*"eGFR"* → *"AGFR"*) | Spoken expanded form disambiguates acronym error; threshold matched. |
| `Q-AERO-14` | Avionics | *"What overall vibration power spectral density must the FCC-900 withstand across 20 Hz to 2,000 Hz?"* | Clean STT | *"7.7 g_rms"* | **Judge Strictness (Partial Credit)** (Cascade Score 1 vs Native Score 2) | Cascade extracted exact correct value (7.7 g_rms); judge docked 1 point for omitting frequency band range. |
| `Q-ONCO-12` | Oncology | *"What age range is eligible for enrollment in the Phase Ib/II trial at screening?"* | Clean STT | *"18 to 80 years old at screening."* | **Judge Strictness (Partial Credit)** (Cascade Score 1 vs Native Score 2) | Correct age range extracted; judge docked 1 point for omitting conversational gender clause. |
| `Q-ONCO-18` | Oncology | *"At what temperature must serum PK aliquots be cryopreserved prior to batch analysis?"* | Clean STT | *"Serum PK aliquots must be cryopreserved at -80.0 deg C."* | **Judge Strictness (Partial Credit)** (Cascade Score 1 vs Native Score 2) | Correct temperature extracted (-80.0 deg C); judge docked 1 point for omitting vapor-phase storage medium. |

---

## 5. Table 5: Architectural Ablation: Context Compression vs. Full Grounding

**Caption:** *Comparative accuracy between intermediate document summarization and full document context injection.*

| Pipeline Configuration | Context Injection Method | Evaluation Set Size | Factual Accuracy | Hallucination Resistance | Combined Benchmark | Mean Inference Latency | Data Source Exhibit |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---|
| **Compressed Context (Baseline)** | Intermediate Gemini Summary (~500 words) | $N=12$ items (9 fact, 3 adv) | **66.7%** (12/18 pts) | **100.0%** (6/6 pts) | **75.0%** (18/24 pts) | 27.179s (p95: 110.454s) | `eval/results_latest.json`, `eval/REPORT.md` |
| **Full Document Context ($N=200$)** | Complete Extracted PDF Text ($\le$50k chars) | $N=200$ items (141 fact, 59 adv) | **100.0%** (Native) / **98.6%** (Cascade) | **100.0%** (Both arms) | **100.0%** (Native) / **99.0%** (Cascade) | 24.511s (Native) / 29.387s (Cascade) | `eval/results_comparison_latest.json` |

---

## 6. Figure 1: Architectural Comparison Flowchart

**Caption:** *System diagram comparing the Native-Audio Multimodal pipeline (top) with the Cascaded STT→LLM pipeline (bottom) for document-grounded spoken QA.*

- **Type:** TikZ / Mermaid vector architecture diagram.
- **Top Lane (Native Arm):** Spoken WAV Audio $\to$ Inline Audio Base64 Streaming $\to$ Google Gemini 3.5 Flash-Lite (Audio + Document Text) $\to$ Multimodal Parser $\to$ [Answer Text + Extracted Vocal Tone].
- **Bottom Lane (Cascade Arm):** Spoken WAV Audio $\to$ Local `faster-whisper-base` (CPU int8) $\to$ Transcribed Text Query $\to$ Google Gemini 3.5 Flash-Lite (Text Only + Document Text) $\to$ Text Parser $\to$ [Answer Text].
- **Data Source Reference:** `eval/COMPARISON_REPORT.md` Section 3.1 & 10.1; `eval/native_arm.py`; `eval/cascade_arm.py`.

---

## 7. Figure 2: End-to-End Latency Distribution and Tail Boxplot ($N = 200$)

**Caption:** *Empirical latency distributions (seconds) across all 200 queries, illustrating local STT efficiency, overall latency parity between arms ($p = 0.470$), and comparison with confounded pilot $N=30$ observations.*

- **Type:** Grouped Boxplot + Jittered Scatter or empirical Cumulative Distribution Function (eCDF).
- **Traces:**
  1. Cascade Total Latency ($N=200$): Mean 29.39s, Median 15.68s, p95 85.32s, Max 118.90s.
  2. Cascade Local STT Latency ($N=200$): Extremely tight band: Mean 0.376s, p95 0.409s, Max 0.540s.
  3. Native Total Latency ($N=200$): Mean 24.51s, Median 14.82s, p95 87.85s, Max 120.49s.
  4. *Reference Inset / Historical Overlay:* Pilot ($N=30$, Free-Tier Confounded) showing Native 33.45s vs Cascade 12.14s.
- **Data Source Reference:** `eval/results_comparison_latest.json` (`itemized_results[*].native.stage_latencies` and `itemized_results[*].cascade.stage_latencies`).

---

## 8. Figure 3: Cost vs. Latency Pareto Frontier ($N = 200$)

**Caption:** *Cost-latency trade-off space for document-grounded spoken QA ($N=200$). The cascaded pipeline matches native audio latency while cutting API operational cost by 87.8% (one-eighth the cost).*

- **Type:** 2D Scatter Plot.
  - X-Axis: Mean End-to-End Latency (seconds) — lower is better.
  - Y-Axis: API Cost per Query (USD) — lower is better.
- **Data Points:**
  - Native Audio ($N=200$): $(24.51\text{s}, \$0.000744/\text{query})$.
  - Cascaded Pipeline ($N=200$): $(29.39\text{s}, \$0.000091/\text{query})$.
- **Visual Callout:** Cascaded pipeline achieves latency parity with 87.8% cost savings ($8.2\times$ cheaper API inference).
- **Data Source Reference:** `eval/results_comparison_latest.json` summary metrics.
