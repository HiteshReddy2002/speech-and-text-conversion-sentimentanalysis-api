# Paper Outline — Speech-to-Text & Sentiment Analysis via Multimodal LLM

**Target venue:** ACL, EMNLP, Interspeech, or NAACL (Student Research Workshop)
**Suggested track:** Short paper (4 pages) or Demo track
**Tentative title:** *Skipping the Transcription Step: Native Audio Understanding for Domain-Specific Document Q&A with Large Language Models*

---

## Abstract (to be written)

*Placeholder — write last, after results section is finalized.*

Key claims to support:
1. Native audio → LLM (multimodal) outperforms STT → LLM (pipeline) for domain-specific question answering accuracy.
2. PyMuPDF + Tesseract OCR fallback provides near-complete PDF coverage with graceful degradation.
3. The combined system achieves 92% QA accuracy on domain-specific PDF evaluation.

---

## 1. Introduction

**Problem statement:**
- Most "talk to your PDF" systems transcribe audio first (STT → text → LLM). This introduces a lossy step that degrades answer quality for domain-specific vocabulary.
- Generic STT models mangle medical, legal, and technical terminology.

**Research question:**
- Does bypassing the STT step and sending raw audio directly to a multimodal LLM improve question-answering accuracy on domain-specific PDFs?

**Contributions:**
1. A multimodal PDF Q&A pipeline that ingests raw WAV audio without transcription.
2. An empirical evaluation of QA accuracy on domain-specific PDFs.
3. An open-source Flask implementation with OCR fallback for scanned documents.

---

## 2. Related Work

*Sections to review and cite:*

- **Document QA systems:** DocVQA, LayoutLM, PDF-QA surveys.
- **Multimodal LLMs:** Gemini 1.5 Pro technical report (Google DeepMind, 2024), GPT-4o audio capabilities.
- **STT → LLM pipelines:** Whisper (Radford et al., 2022); cascaded vs. end-to-end ASR comparisons.
- **RAG for document QA:** Lewis et al. (2020), "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks."
- **OCR in document understanding:** Tesseract (Smith, 2007); PaddleOCR comparisons.

---

## 3. System Architecture and Methods

**3.1 PDF Text Extraction**
- Primary: PyMuPDF `page.get_text()` — digital PDFs.
- Fallback: `pdf2image` (Poppler) + `pytesseract` — scanned PDFs.
- Decision criterion: `if not extracted_text.strip()` → invoke OCR.

**3.2 Document Summarization**
- Gemini 1.5 Pro with 10,000-character truncation window.
- Prompt: "Summarize the following text briefly."
- Limitation: does not handle documents > 10K chars gracefully (acknowledged; RAG is the solution).

**3.3 Native Audio QA**
- WAV bytes sent as `inline_data` to Gemini 1.5 Pro.
- No intermediate transcription.
- Prompt template: "You are a helpful assistant. Use the summary of the uploaded book and answer the user's audio question."

**3.4 Text-to-Speech Response**
- Google Cloud TTS, Neural2 voice, MP3 encoding.
- Both text transcript and audio file returned to client.

**3.5 Baseline comparison (to be implemented for paper):**
- System A (proposed): raw audio → Gemini multimodal
- System B (baseline): Whisper STT → text → Gemini text-only

---

## 4. Experiments

**4.1 Dataset**
- 5 domain-specific PDF documents (medical, legal, technical, academic, financial).
- 50 question-answer pairs (10 per domain), manually annotated.
- Answer correctness judged by human annotators (binary: correct / incorrect).
- Annotation protocol: TO BE DEFINED (inter-annotator agreement metric: Cohen's κ).

**4.2 Evaluation Metrics**
- Primary: QA Accuracy (% of answers rated correct by annotators).
- Secondary: Response latency (time from audio upload to JSON response, excluding TTS).
- Tertiary: OCR fallback rate (% of PDFs requiring OCR).

**4.3 Current Results**
- QA Accuracy (System A, proposed): **92%** (46/50 correct).
- Baseline (System B): TO BE MEASURED (needed for paper).
- OCR fallback rate: TO BE MEASURED.
- Response latency: TO BE MEASURED systematically.

---

## 5. Results and Discussion

*To be written after baseline comparison experiments are run.*

Planned discussion points:
- Cases where native audio outperformed STT baseline (expected: technical terminology).
- Cases where native audio failed (expected: heavy background noise, non-English audio).
- Truncation limitation impact on long-document accuracy.
- Comparison of OCR quality across document types.

---

## 6. Conclusion

*To be written last.*

Key points to include:
- Multimodal LLMs reduce cascaded error in voice-based document QA.
- Open-source implementation enables reproducibility and extension.
- Future work: RAG-based retrieval for long documents; LSTM/RNN for streaming audio.

---

## References

*To be populated during related work review. Use ACL Anthology BibTeX format.*

---

## Appendix

- System prompts (verbatim, for reproducibility).
- Annotator guidelines for QA evaluation.
- Full evaluation dataset (if publishable; check PDF copyright for domain documents).
