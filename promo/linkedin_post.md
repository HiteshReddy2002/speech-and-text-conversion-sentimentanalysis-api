# LinkedIn Post Draft — Speech & Sentiment API
*[Draft — ~170 words | DO NOT PUBLISH without explicit approval]*

---

I built a multimodal document Q&A app where you **speak your question** and get a **spoken answer** — entirely powered by Google Gemini 1.5 Pro and Google Cloud TTS.

Upload a PDF. Record a question. Get an audio response back.

What makes it interesting:
→ Gemini processes raw audio bytes natively — no lossy STT transcription step
→ PyMuPDF for digital PDFs + Tesseract OCR fallback for scanned documents
→ 92% answer accuracy on domain-specific PDF evaluation
→ Production Flask API with gunicorn, structured logging, Procfile

The biggest lesson: **always load API keys from environment variables, never from source code**. I learned that the hard way.

The full source, architecture diagram (Mermaid), quickstart guide, and HuggingFace Spaces deployment instructions are open-sourced on GitHub.

🔗 github.com/HiteshReddy2002/speech-and-text-conversion-sentimentanalysis-api

What would you add — streaming audio responses? RAG-based retrieval over long documents?

#Python #NLP #GoogleCloud #Gemini #MachineLearning #OpenSource
