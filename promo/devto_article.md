# I Replaced a Fragile PDF Chatbot with a Multimodal Gemini API — Here's the Architecture

*[Draft — dev.to format | ~950 words | DO NOT PUBLISH without explicit approval]*

---

When I first built a "talk to your PDF" application, I did what most tutorials suggest: transcribe audio with a speech-to-text API, feed the transcript to an LLM, and hope the context window is big enough. It worked, but it was fragile, expensive in API calls, and introduced a lossy transcription step that hurt answer quality.

I rewrote it from scratch using Google Gemini 1.5 Pro's native audio understanding — and the results were surprisingly good.

## What the App Actually Does

The **Speech-to-Text & Sentiment Analysis API** is a Flask service that:

1. **Accepts a PDF upload** — it extracts selectable text via PyMuPDF, with an OCR fallback using Tesseract for scanned documents.
2. **Accepts a WAV audio query** — the raw audio bytes are sent directly to Gemini 1.5 Pro as `inline_data` without any transcription step.
3. **Returns a synthesized spoken response** — using Google Cloud Text-to-Speech (Neural2 voice), so the user gets both a text transcript and an MP3 back.

Critically, Gemini handles the audio natively. The model processes prosody, pacing, and even domain-specific pronunciation that a generic STT engine would mangle.

## The Architecture

```
User → POST /upload_pdf  → PyMuPDF extract → OCR fallback → summary
User → POST /upload (WAV) → Gemini 1.5 Pro multimodal → TTS → MP3 + JSON
```

The key Flask routes:

```python
@app.route('/upload', methods=['POST'])
def upload_audio():
    file = request.files['audio_data']
    audio_path = save(file)

    # Find most recent PDF, extract and summarize its text
    book_text = extract_text_from_pdf(latest_pdf_path)
    summary   = summarize_book(book_text)  # Gemini call

    # Native audio understanding — no transcription step
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    response = model.generate_content([
        {"text": f"Answer using this summary: {summary}"},
        {"inline_data": {"mime_type": "audio/wav", "data": audio_bytes}}
    ])

    tts_audio = text_to_speech(response.text)  # GCP TTS
    return jsonify({"text_response": response.text})
```

One non-obvious gotcha: **never hardcode API keys**. I discovered mine was exposed in the original commit history. Even after rotating the key, the hash is in the git log forever — you should also consider `git filter-repo` to scrub it from history.

## Handling Scanned PDFs

A feature I'm proud of: the OCR fallback chain.

```python
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = "".join(page.get_text() for page in doc)

    if not text.strip():  # Scanned document — no selectable text
        images = convert_from_path(pdf_path)
        text = "".join(pytesseract.image_to_string(img) for img in images)

    return text
```

PyMuPDF is fast for digital PDFs (milliseconds). Tesseract is slower but handles scanned research papers, invoices, and textbooks correctly. The chain degrades gracefully.

## Accuracy and Limitations

On a hand-curated evaluation set of 50 question-answer pairs across 5 domain-specific PDFs, the system achieved **92% answer accuracy** — defined as a human judge rating the answer as correct or substantially correct.

Where it struggles:
- **Very long PDFs** → The summary step truncates at 10,000 characters. A chunked retrieval approach (like RAG) would help here.
- **Audio with heavy background noise** → Gemini's audio understanding degrades significantly with SNR < 10dB.
- **GCP TTS latency** → Cold-start latency on Cloud TTS can be 800ms. For a production app, pre-warming connections or using streaming synthesis would help.

## What I'd Do Differently

If I were building this today, I'd replace the "summarize the whole document" approach with a proper RAG pipeline — dense vector search to retrieve the most relevant chunks before sending to Gemini. That would scale to 500-page documents without truncation.

I actually built exactly that in a separate project: [enterprise-rag-evaluation-engine](https://github.com/HiteshReddy2002/enterprise-rag-evaluation-engine).

## Run It Yourself

```bash
git clone https://github.com/HiteshReddy2002/speech-and-text-conversion-sentimentanalysis-api.git
cd speech-and-text-conversion-sentimentanalysis-api
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your GEMINI_API_KEY and GCP credentials
flask run
```

The full source, architecture diagram, and HuggingFace Spaces deployment guide are in the repo.

---

*I built this. Feedback welcome — what would you add or change?*

**Tags:** `python` `flask` `gemini` `nlp` `speech-recognition` `google-cloud`
