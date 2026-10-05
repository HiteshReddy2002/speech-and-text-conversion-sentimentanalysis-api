"""
Gradio demo for the Speech-to-Text & Sentiment Analysis API.

Imports from the repo's actual modules (main.py helpers) wherever possible.
For credential-requiring functions (Gemini, GCP TTS), the demo uses a 'mock'
mode when API keys are absent so the UI still loads cleanly on HuggingFace.
"""

import os
import sys
import tempfile
import pathlib

# Allow imports from parent directory
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import gradio as gr

# ── Attempt real imports; fall back to mock if credentials are missing ─────

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
GCP_CREDS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")

MOCK_MODE = not GEMINI_KEY  # Use mock responses if no key configured

if not MOCK_MODE:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_KEY)
        from main import extract_text_from_pdf, summarize_book
        MOCK_MODE = False
    except Exception as e:
        print(f"[WARN] Could not import live modules: {e}. Using mock mode.")
        MOCK_MODE = True


# ── Helper functions ────────────────────────────────────────────────────────

def _mock_summarize(text: str) -> str:
    words = text.split()[:60]
    return "Mock summary: " + " ".join(words) + " [... demo mode, no API key set]"


def _mock_answer(summary: str, question: str) -> str:
    return (
        f"Mock answer for '{question}': Based on the document summary, "
        "this is a demonstration response. Set GEMINI_API_KEY to enable "
        "real Gemini-powered answers."
    )


def process_pdf_and_question(pdf_file, text_question: str):
    """Main handler: extract PDF text, summarize, answer the question."""
    if pdf_file is None:
        return "Please upload a PDF first.", "", ""

    if not text_question.strip():
        return "Please type a question.", "", ""

    # Extract text from PDF
    pdf_path = pdf_file.name if hasattr(pdf_file, "name") else str(pdf_file)

    try:
        if MOCK_MODE:
            import fitz
            doc = fitz.open(pdf_path)
            raw_text = "".join(p.get_text() for p in doc)
            summary = _mock_summarize(raw_text)
            answer = _mock_answer(summary, text_question)
        else:
            raw_text = extract_text_from_pdf(pdf_path)
            summary = summarize_book(raw_text)
            import google.generativeai as genai
            model_name = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")
            model = genai.GenerativeModel(model_name)
            resp = model.generate_content([
                {"text": f"Based on the following document, answer the question accurately with exact metrics and bounds:\n\n{raw_text[:50000]}\n\nQuestion: {text_question}"}
            ])
            answer = resp.text
    except Exception as e:
        return f"Error: {e}", "", ""

    sentiment = analyze_sentiment(answer)
    return summary, answer, sentiment


def analyze_sentiment(text: str) -> str:
    """Simple keyword-based sentiment for demo (no external dependency)."""
    positive_words = {"great", "excellent", "good", "positive", "success", "helpful", "accurate", "clear"}
    negative_words = {"bad", "poor", "error", "fail", "negative", "wrong", "issue", "problem"}
    words = set(text.lower().split())
    pos = len(words & positive_words)
    neg = len(words & negative_words)
    if pos > neg:
        return f"Positive (score: +{pos})"
    elif neg > pos:
        return f"Negative (score: -{neg})"
    return "Neutral"


# ── Gradio UI ───────────────────────────────────────────────────────────────

MODE_BADGE = "🔴 MOCK MODE (no API key)" if MOCK_MODE else "🟢 LIVE (Gemini connected)"

with gr.Blocks(title="Speech & Sentiment API Demo", theme=gr.themes.Soft()) as demo:
    gr.Markdown(f"""
    # 🎙️ Speech-to-Text & Sentiment Analysis API
    **Demo** | {MODE_BADGE}

    Upload a PDF document, type your question, and get a Gemini-powered answer
    with sentiment analysis. Set `GEMINI_API_KEY` to enable live responses.

    > **Source**: [HiteshReddy2002/speech-and-text-conversion-sentimentanalysis-api](https://github.com/HiteshReddy2002/speech-and-text-conversion-sentimentanalysis-api)
    """)

    with gr.Row():
        with gr.Column(scale=1):
            pdf_input = gr.File(label="Upload PDF", file_types=[".pdf"])
            question_input = gr.Textbox(
                label="Your Question",
                placeholder="What is the main topic of this document?",
                lines=3,
            )
            submit_btn = gr.Button("🔍 Ask", variant="primary")

        with gr.Column(scale=2):
            summary_output = gr.Textbox(label="Document Summary", lines=6, interactive=False)
            answer_output = gr.Textbox(label="Answer", lines=6, interactive=False)
            sentiment_output = gr.Textbox(label="Response Sentiment", interactive=False)

    submit_btn.click(
        fn=process_pdf_and_question,
        inputs=[pdf_input, question_input],
        outputs=[summary_output, answer_output, sentiment_output],
    )

    gr.Examples(
        examples=[["", "What is the main conclusion of this document?"]],
        inputs=[pdf_input, question_input],
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
