# Work-Back Schedule: Interspeech 2027 Workshop Track

**Target Venue:** Interspeech 2027 (Workshop Track on Trustworthy Speech Processing)  
**Target Submission Deadline:** Monday, February 9, 2027 (23:59 AoE)  
**Current Date:** October 6, 2026  
**Total Preparation Window:** 18 Weeks  
**Primary Milestones:**
- **Mid-Dec 2026:** Complete Full Draft (LaTeX / Overleaf)
- **Jan 2027:** Internal Review, Revisions, & Secondary Experiments
- **Early Feb 2027:** Submission Buffer & Final Freeze

---

## Weekly Work-Back Breakdown

### Phase 1: Foundation, Infrastructure, & Load-Bearing Experiments (Weeks 1–6)
*Target: Resolve load-bearing experimental gaps and freeze quantitative results.*

- **Week 1 (Oct 6 – Oct 13, 2026) — Paper Skeleton & Baseline Verification [COMPLETED]**
  - [x] Complete evidence audit across all raw JSON results.
  - [x] Write `paper/OUTLINE.md`, `paper/ABSTRACT_DRAFT.md`, `paper/FIGURES_PLAN.md`, `paper/RELATED_WORK.md`, `paper/TIMELINE.md`.
  - [x] Create branch `agent/paper-skeleton` and pull request.

- **Week 2 (Oct 13 – Oct 20, 2026) — Live TTS Instrumentation (`TODO-3`)**
  - [ ] Configure Google Cloud Text-to-Speech service-account credentials in sandbox.
  - [ ] Measure live Google Cloud TTS synthesis latency (mean, p95, bandwidth) across all 30 responses.
  - [ ] Update Table 2 latency breakdown with end-to-end spoken-in / spoken-out timings.

- **Week 3 (Oct 20 – Oct 27, 2026) — Acoustic Diversity & Noise Evaluation (`TODO-1`)**
  - [ ] Collect multi-accent speech samples (clean, non-native accents).
  - [ ] Inject calibrated acoustic noise (clean, 20 dB SNR, 10 dB SNR white/babble noise).
  - [ ] Evaluate boundary WER threshold where Whisper degradation degrades downstream QA accuracy.

- **Week 4 (Oct 27 – Nov 3, 2026) — Dataset Scaling to $N \ge 100$ (`TODO-2` Part 1)**
  - [ ] Curate 2 additional domain documents (aerospace flight manual, legal agreement).
  - [ ] Generate 70 additional questions (50 factual, 20 adversarial unanswerable).
  - [ ] Synthesize offline audio and run batch benchmark runner.

- **Week 5 (Nov 3 – Nov 10, 2026) — Scaled Benchmark Freeze & Statistical Tests (`TODO-2` Part 2)**
  - [ ] Finalize full benchmark run ($N \ge 150$--$200$ items).
  - [ ] Compute bootstrap 95% confidence intervals on latency, cost, and accuracy parity.
  - [ ] Run McNemar's test on accuracy and Wilcoxon signed-rank test on latency distributions.

- **Week 6 (Nov 10 – Nov 17, 2026) — Quantitative Data Freeze & Figure Generation**
  - [ ] Finalize Table 1 (Accuracy), Table 2 (Latency), Table 3 (Cost), and Table 4 (Phonetic Repair).
  - [ ] Generate publication-ready vector figures: Figure 1 (TikZ Architecture), Figure 2 (Latency eCDF/Boxplot), Figure 3 (Cost-Latency Pareto Frontier).
  - [ ] Freeze `results_final.json` and release data artifacts in repository.

---

### Phase 2: Full Prose Drafting in LaTeX (Weeks 7–10)
*Target: Produce a complete, polished 4-page manuscript by mid-December.*

- **Week 7 (Nov 17 – Nov 24, 2026) — Methodology & Empirical Results Sections**
  - [ ] Set up Interspeech 2027 LaTeX template on Overleaf.
  - [ ] Draft Section 3: *System Architectures & Experimental Rig* (Native arm, Cascade arm, Prompt templates).
  - [ ] Draft Section 4: *Empirical Results* (Accuracy tie, latency reduction, cost economics).

- **Week 8 (Nov 24 – Dec 1, 2026) — Failure Analysis & Acoustic Distortion Case Studies**
  - [ ] Draft Section 5: *Acoustic Distortion and Semantic Context Recovery* (detailed phonetic case studies: *"slough or rot"*, *"AGFR"*, *"hypertension"*).
  - [ ] Draft Section 4.4: *Context Compression Ablation* (66.7% vs. 100% summarization analysis).

- **Week 9 (Dec 1 – Dec 8, 2026) — Introduction, Related Work, & Limitations**
  - [ ] Draft Section 1: *Introduction* (Problem statement, research questions, summary of contributions).
  - [ ] Draft Section 2: *Related Work* (integrate 5 verified core citations).
  - [ ] Draft Section 6: *Limitations & Threats to Validity*.
  - [ ] Draft Section 7: *Conclusion*.

- **Week 10 (Dec 8 – Dec 15, 2026) — MILESTONE: FULL DRAFT TARGET (Mid-Dec 2026)**
  - [ ] Assemble complete 4-page paper draft + 1-page references + supplementary appendix.
  - [ ] Verify abstract adheres to 150–200 words and matches draft in `paper/ABSTRACT_DRAFT.md`.
  - [ ] Internal sanity check: ensure zero unverified numbers or fabricated citations.

---

### Phase 3: Internal Review & Secondary Enhancements (Weeks 11–14)
*Target: Solicit peer critique, conduct nice-to-have validations, and tighten arguments.*

- **Week 11 (Dec 15 – Dec 22, 2026) — Internal Peer Review Distribution**
  - [ ] Send complete manuscript draft to 2–3 colleagues (speech processing, NLP, and system engineering).
  - [ ] Solicit specific feedback on framing (efficiency vs. accuracy parity) and tone.

- **Week 12 (Dec 22 – Dec 29, 2026) — Human Inter-Annotator Agreement (`TODO-5`)**
  - [ ] Run dual-annotator human evaluation on subset of answers.
  - [ ] Calculate Cohen's $\kappa$ against Gemini 3.1 Flash-Lite judge.
  - [ ] Holiday week buffer.

- **Week 13 (Dec 29, 2026 – Jan 5, 2027) — Cross-Model Generalization (`TODO-4`)**
  - [ ] Benchmark alternative ASR model (`whisper-large-v3` or `whisper.cpp`) on subset to confirm latency scaling.
  - [ ] Add brief paragraph in Discussion confirming generalizability across speech models.

- **Week 14 (Jan 5 – Jan 12, 2027) — Review Feedback Integration & Page Budgeting**
  - [ ] Collate internal review comments and formulate revision plan.
  - [ ] Compress text to strictly respect Interspeech 4-page limit (+ 1 page references).

---

### Phase 4: Final Revisions & Camera-Ready Formatting (Weeks 15–16)
*Target: Perfect typography, verify compliance, and finalize open-source repository.*

- **Week 15 (Jan 12 – Jan 19, 2027) — Polish & Quality Audit**
  - [ ] Typography check: check table formatting (`booktabs`), font sizes, vector figure resolutions.
  - [ ] Verify all citations against official ACL Anthology and arXiv DOIs.
  - [ ] Confirm traceability of every number back to repo JSON exhibits.

- **Week 16 (Jan 19 – Jan 26, 2027) — Open-Source Code & Reproducibility Release**
  - [ ] Clean up public branch, test fresh clone on Linux and Windows.
  - [ ] Verify `eval/run_comparison.py` runs end-to-end out-of-the-box.
  - [ ] Tag reproducibility release in GitHub (e.g., `v1.0.0-paper-interspeech2027`).

---

### Phase 5: Submission Buffer & Portal Freeze (Weeks 17–18)
*Target: Early submission without deadline pressure.*

- **Week 17 (Jan 26 – Feb 2, 2027) — MILESTONE: SUBMISSION BUFFER**
  - [ ] Run PDF eXpress / Interspeech PDF compliance checker (embedded fonts, margins, page limits).
  - [ ] Prepare OpenReview / CMT submission metadata (abstract, keywords, subject areas).
  - [ ] Package anonymous supplementary code and evaluation audio repository.

- **Week 18 (Feb 2 – Feb 9, 2027) — Final Upload & Submission Freeze**
  - [ ] Final author read-through.
  - [ ] Upload final PDF and supplementary materials by Feb 6 (3 days before Feb 9 deadline).
  - [ ] **Feb 9, 2027: Official Workshop Submission Deadline.**

---

## Risk Register & Mitigation Strategy

| Risk ID | Potential Impact | Severity | Mitigation Strategy |
|:---|:---|:---:|:---|
| **R-1** | GCP TTS API latency cannot be measured due to credential limits | Low | TTS is orthogonal to the core STT vs. Native query ingestion claim; document TTS as modular additive latency if unconfigured. |
| **R-2** | Scaling from $N=30$ to $N=200$ introduces Whisper failures that break accuracy parity | Medium | This strengthens the scientific value of the paper! It precisely maps the boundary conditions where document priors fail, turning a limitation into a primary contribution. |
| **R-3** | Reviewer questions LLM-as-judge validity | Medium | Mitigated by Phase 3 human annotation agreement experiment (`TODO-5`) proving high Cohen's $\kappa$ ($> 0.85$). |
| **R-4** | Interspeech page limit overflow (4 pages) | Medium | Figures 2 and 3 can be combined or moved to the supplementary appendix; core tables condensed using standard abbreviations. |
