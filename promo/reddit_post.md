# Reddit Post Draft — r/MachineLearning
*[Draft — DO NOT PUBLISH without explicit approval]*

---

**Title:** I built a multimodal PDF Q&A system using Gemini 1.5 Pro's native audio understanding — skipping the STT step entirely [I built this]

---

**Body:**

I built this for a course project and wanted to share the architecture since I found the "native audio" approach non-obvious.

**What it does:** You upload a PDF, record a WAV question, and get a text + audio answer back. Standard stuff. The twist is that instead of transcribing the audio first (speech-to-text → text → LLM), I send the raw WAV bytes directly to Gemini 1.5 Pro as `inline_data`. The model handles audio understanding natively.

**Why this matters:** A traditional STT → LLM pipeline introduces two points of failure — transcription errors compound into worse answers. For domain-specific vocabulary (medical, legal, technical), generic STT models frequently mangle terminology. Gemini handles it better end-to-end in my evaluation.

**Accuracy:** 92% on a 50-question eval set across 5 domain-specific PDFs. Not peer-reviewed, just manual annotation.

**Stack:** Flask, PyMuPDF (with Tesseract OCR fallback for scanned PDFs), `google-generativeai`, `google-cloud-texttospeech`, gunicorn.

**Known limitations:**
- Truncates PDFs at 10,000 chars before summarizing — would need RAG for long docs
- GCP TTS has ~800ms cold-start latency
- No streaming audio yet

**Source:** https://github.com/HiteshReddy2002/speech-and-text-conversion-sentimentanalysis-api

Honest question for the sub: is the "native audio" approach to multimodal QA well-studied? I couldn't find much literature on comparing STT-then-LLM vs. native audio LLM for domain-specific accuracy. Would be curious if anyone has done a more rigorous benchmark.
