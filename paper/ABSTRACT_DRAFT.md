# Abstract Draft: Interspeech 2027 Workshop Track

**Target Length:** 150–200 words  
**Word Count:** 176 words (excluding title and metadata)  
**Status:** Grounded strictly in repository exhibits (`eval/results_comparison_latest.json`, `eval/COMPARISON_REPORT.md` Section 10)  
**Core Thesis:** Cascaded pipelines match native-audio models on accuracy and latency for document-grounded spoken QA, at one-eighth the API cost.

---

### Abstract

Multimodal large language models increasingly support direct speech ingestion, challenging traditional cascaded pipelines (speech recognition followed by text language models). We present a rigorous head-to-head empirical comparison of a native-audio model (Gemini 3.5 Flash-Lite) against a cascaded pipeline (faster-whisper-base and Gemini 3.5 Flash-Lite) on document-grounded spoken question answering across 200 technical queries (141 factual, 59 adversarial) spanning eight domains. We find that cascaded pipelines match native-audio models on accuracy and latency for document-grounded spoken QA, at one-eighth the API cost. On factual retrieval, both architectures exhibit statistical parity (native 100.0% vs. cascade 98.6%, McNemar p=0.125), with intermediate transcription errors reliably repaired by dense document priors; both achieve 100.0% adversarial hallucination resistance. Correcting an earlier pilot finding confounded by free-tier API throttling, end-to-end latency between the architectures is statistically indistinguishable (cascade 29.39s vs. native 24.51s, Wilcoxon p=0.470), with local CPU transcription adding merely 0.38s. However, cascaded processing yields an 87.8% API cost reduction ($0.01814 vs. $0.14889, 95% CI [-88.1%, -87.4%]) due to text token pricing. In document-grounded settings, lightweight cascades achieve full parity without native-audio cost premiums.

---

### Exhibit Audit for Abstract Numbers

| Claimed Metric in Abstract | Exact Value | Source File | JSON Key / Report Line |
|:---|:---:|:---|:---|
| Total Queries Evaluated | 200 (141 factual, 59 adversarial) | `eval/results_comparison_latest.json` | `total_questions`, `factual_questions`, `adversarial_questions` |
| Technical Domains / Documents | 8 domains (25 items each) | `eval/dataset_v2.csv`, `eval/COMPARISON_REPORT.md` | Section 10.1 & 10.4 |
| Native Factual Accuracy | 100.0% (282/282 points) | `eval/results_comparison_latest.json` | `summary_metrics.native.factual_accuracy_pct` |
| Cascade Factual Accuracy | 98.6% (278/282 points) | `eval/results_comparison_latest.json` | `summary_metrics.cascade.factual_accuracy_pct` |
| Factual Accuracy McNemar Test | $p = 0.12500$ ($\chi^2 = 2.25$, not significant) | `eval/analyze_n200.py`, `eval/COMPARISON_REPORT.md` | Section 10.2 & 10.3 |
| Native Adversarial Abstention | 100.0% (59/59 refused) | `eval/results_comparison_latest.json` | `summary_metrics.native.abstention_rate_pct` |
| Cascade Adversarial Abstention | 100.0% (59/59 refused) | `eval/results_comparison_latest.json` | `summary_metrics.cascade.abstention_rate_pct` |
| Adversarial Abstention McNemar | $p = 1.00000$ (0 discordant pairs) | `eval/analyze_n200.py`, `eval/COMPARISON_REPORT.md` | Section 10.2 & 10.3 |
| Native Mean Latency | 24.511s (p95: 87.845s) | `eval/results_comparison_latest.json` | `summary_metrics.native.latencies.total.mean` |
| Cascade Mean Latency | 29.387s (p95: 85.316s) | `eval/results_comparison_latest.json` | `summary_metrics.cascade.latencies.total.mean` |
| Latency Wilcoxon Test | $W = 9566.0, z = +0.722, p = 0.470$ | `eval/analyze_n200.py`, `eval/COMPARISON_REPORT.md` | Section 10.2 & 10.3 |
| Local STT Overhead (faster-whisper) | 0.376s mean (p95: 0.409s) | `eval/results_comparison_latest.json` | `summary_metrics.cascade.latencies.stt.mean` |
| Native API Token Cost | $0.14889 USD (220,059 tokens) | `eval/results_comparison_latest.json` | `summary_metrics.native.estimated_api_cost_usd` |
| Cascade API Token Cost | $0.01814 USD (164,143 tokens) | `eval/results_comparison_latest.json` | `summary_metrics.cascade.estimated_api_cost_usd` |
| API Cost Reduction | 87.8% (-$0.13075 USD) | `eval/results_comparison_latest.json` | `summary_metrics.deltas.cost_delta_usd` |
| Cost Delta Bootstrap 95% CI | [-88.1%, -87.4%] / [-$0.1345, -$0.1268] | `eval/analyze_n200.py`, `eval/COMPARISON_REPORT.md` | Section 10.3 |
| Pilot N=30 Throttling Confound | 63.7% latency advantage artifact | `eval/COMPARISON_REPORT.md` | Section 1 & Section 10.2 |
