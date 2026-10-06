# Abstract Draft: Interspeech 2027 Workshop Track

**Target Length:** 150–200 words  
**Word Count:** 178 words (excluding title and metadata)  
**Status:** Grounded strictly in repo exhibits (`eval/results_comparison_latest.json`, `eval/REPORT.md`)  
**Core Thesis:** Efficiency dominance of cascaded pipelines under grounded accuracy parity; context compression as accuracy bottleneck.

---

### Abstract

Multimodal large language models increasingly support native speech ingestion, challenging traditional cascaded pipelines (speech recognition followed by text language models). We present an empirical head-to-head comparison of a native-audio model (Gemini 3.1 Flash-Lite) against a cascaded pipeline (faster-whisper-base and Gemini 3.1 Flash-Lite) on document-grounded spoken question answering across 30 domain-specific queries (21 factual, 9 adversarial). Contrary to assumptions of acoustic superiority, both architectures achieved identical 100.0% factual accuracy and 100.0% adversarial abstention when grounded on full document context. Despite acoustic transcription errors in the cascaded arm, dense document priors enabled the downstream language model to reliably repair phonetic corruptions. However, the cascaded pipeline demonstrated decisive efficiency advantages, reducing mean end-to-end latency by 63.7% (12.14s versus 33.45s), p95 latency by 65.1% (24.97s versus 71.63s), and theoretical API cost by 88.0% ($0.00239 versus $0.01984). Furthermore, an architectural ablation reveals that intermediate document compression, rather than speech modeling, was the true accuracy bottleneck, lifting factual accuracy from 66.7% under summarization to 100.0% under full context. For grounded spoken understanding, lightweight cascaded architectures provide superior speed and economics without compromising task accuracy.

---

### Exhibit Audit for Abstract Numbers

| Claimed Metric in Abstract | Exact Value | Source File | JSON Key / Report Line |
|:---|:---:|:---|:---|
| Total Queries Evaluated | 30 (21 factual, 9 adversarial) | `eval/results_comparison_latest.json` | `total_questions`, `factual_questions`, `adversarial_questions` |
| Native Factual Accuracy | 100.0% (42/42 points) | `eval/results_comparison_latest.json` | `summary_metrics.native.factual_accuracy_pct` |
| Cascade Factual Accuracy | 100.0% (42/42 points) | `eval/results_comparison_latest.json` | `summary_metrics.cascade.factual_accuracy_pct` |
| Native Adversarial Abstention | 100.0% (9/9 items) | `eval/results_comparison_latest.json` | `summary_metrics.native.abstention_rate_pct` |
| Cascade Adversarial Abstention | 100.0% (9/9 items) | `eval/results_comparison_latest.json` | `summary_metrics.cascade.abstention_rate_pct` |
| Native Mean Latency | 33.450s | `eval/results_comparison_latest.json` | `summary_metrics.native.latencies.total.mean` |
| Cascade Mean Latency | 12.136s | `eval/results_comparison_latest.json` | `summary_metrics.cascade.latencies.total.mean` |
| Mean Latency Reduction | 63.7% (-21.314s) | `eval/results_comparison_latest.json` | `summary_metrics.deltas.mean_latency_delta_sec` |
| Native p95 Latency | 71.633s | `eval/results_comparison_latest.json` | `summary_metrics.native.latencies.total.p95` |
| Cascade p95 Latency | 24.969s | `eval/results_comparison_latest.json` | `summary_metrics.cascade.latencies.total.p95` |
| p95 Latency Reduction | 65.1% (-46.664s) | `eval/results_comparison_latest.json` | Computed from `latencies.total.p95` |
| Native API Token Cost | $0.01984 USD | `eval/results_comparison_latest.json` | `summary_metrics.native.estimated_api_cost_usd` |
| Cascade API Token Cost | $0.00239 USD | `eval/results_comparison_latest.json` | `summary_metrics.cascade.estimated_api_cost_usd` |
| API Cost Reduction | 88.0% (-$0.01745 USD) | `eval/results_comparison_latest.json` | `summary_metrics.deltas.cost_delta_usd` |
| Summarization Baseline Factual Acc | 66.7% (12/18 points) | `eval/results_latest.json` / `eval/REPORT.md` | `eval/REPORT.md` Section 1 & Section 3.1 |
