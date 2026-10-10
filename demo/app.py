"""
Gradio demo for the Speech-to-Text & Sentiment Analysis API.

Demonstrates document-grounded spoken question answering using native audio input
(microphone or audio file) alongside text query fallback. Reuses the core pipeline
from main.py (extract_text_from_pdf, summarize_book, process_query_with_llm).

In LIVE mode (GEMINI_API_KEY configured):
  - Spoken audio WAV is ingested natively by Gemini Flash-Lite alongside PDF context.
  - Returns grounded answer text and extracts acoustic vocal tone/sentiment.
In MOCK mode (no GEMINI_API_KEY):
  - Clear, unmissable mock responses labeled as demo/simulated (never fakes transcription).
"""

import os
import sys
import wave
import shutil
import logging
import tempfile
import pathlib
import subprocess
from typing import Tuple, Optional

# Allow imports from parent directory or current directory
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).parent))

import gradio as gr

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("demo_app")

# ── Gemini Credentials & Live Pipeline Imports ───────────────────────────────

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
MOCK_MODE = not bool(GEMINI_KEY)

# Attempt live imports from main.py
try:
    from main import (
        extract_text_from_pdf,
        summarize_book,
        process_query_with_llm,
        GEMINI_MODEL,
        MAX_DOCUMENT_CHARS,
    )
    import google.generativeai as genai
    if not MOCK_MODE:
        genai.configure(api_key=GEMINI_KEY)
        logger.info("🟢 Live Gemini API configured successfully.")
    else:
        logger.info("🔴 No GEMINI_API_KEY found. Running in MOCK mode.")
except Exception as import_err:
    logger.warning(f"Failed to import live modules from main.py: {import_err}. Defaulting to MOCK mode.")
    MOCK_MODE = True
    GEMINI_MODEL = "gemini-3.5-flash-lite"
    MAX_DOCUMENT_CHARS = 50000


# ── Audio Format Preparation & Honest Validation ─────────────────────────────

def prepare_audio_for_gemini(audio_path: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Validates that audio is a valid 16-bit PCM WAV for Gemini inline_data ingestion.
    If input is WebM/MP3/OGG or non-standard WAV, attempts conversion via pydub or ffmpeg.
    Explicitly logs every step and returns (wav_path, error_message).
    """
    if not audio_path or not os.path.exists(audio_path):
        return None, "Audio recording was not received or the temporary file was not found."

    file_size = os.path.getsize(audio_path)
    if file_size < 100:
        return None, f"Audio recording is empty or corrupted ({file_size} bytes received)."

    logger.info(f"[Audio] Inspecting input file: {audio_path} ({file_size} bytes)")

    # 1. Check if already a valid standard PCM WAV
    try:
        with wave.open(audio_path, "rb") as wf:
            channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            framerate = wf.getframerate()
            nframes = wf.getnframes()
            duration = nframes / float(framerate) if framerate > 0 else 0.0

            logger.info(
                f"[Audio] Valid PCM WAV header verified: {channels} ch, {sampwidth * 8}-bit, "
                f"{framerate} Hz, duration: {duration:.2f}s."
            )
            # If 16-bit PCM (sampwidth == 2), return directly
            if sampwidth == 2:
                return audio_path, None
            else:
                logger.info(f"[Audio] Non-16-bit WAV detected ({sampwidth * 8}-bit). Resampling required.")
    except Exception as wave_err:
        logger.info(f"[Audio] Input is not standard PCM WAV ({wave_err}). Conversion required.")

    # 2. Conversion required: try pydub or ffmpeg
    converted_path = tempfile.NamedTemporaryFile(delete=False, suffix="_gemini_16k.wav").name
    conversion_errors = []

    # Attempt A: pydub
    try:
        from pydub import AudioSegment
        logger.info(f"[Audio] Converting via pydub: {audio_path} -> {converted_path}")
        seg = AudioSegment.from_file(audio_path)
        seg = seg.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        seg.export(converted_path, format="wav")
        with wave.open(converted_path, "rb") as verify_wf:
            logger.info(f"[Audio] pydub conversion verified: {verify_wf.getframerate()} Hz, 16-bit mono WAV.")
            return converted_path, None
    except Exception as e:
        conversion_errors.append(f"pydub: {e}")
        logger.warning(f"[Audio] pydub conversion failed: {e}")

    # Attempt B: ffmpeg CLI
    ffmpeg_bin = shutil.which("ffmpeg")
    if ffmpeg_bin:
        try:
            logger.info(f"[Audio] Converting via ffmpeg CLI: {audio_path} -> {converted_path}")
            subprocess.run(
                [
                    ffmpeg_bin, "-y", "-i", audio_path,
                    "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
                    converted_path
                ],
                check=True,
                capture_output=True,
                text=True
            )
            with wave.open(converted_path, "rb") as verify_wf:
                logger.info(f"[Audio] ffmpeg conversion verified: {verify_wf.getframerate()} Hz, 16-bit mono WAV.")
                return converted_path, None
        except Exception as e:
            conversion_errors.append(f"ffmpeg: {e}")
            logger.warning(f"[Audio] ffmpeg conversion failed: {e}")
    else:
        conversion_errors.append("ffmpeg CLI binary not available in system PATH")

    # If all conversion attempts failed, return honest error
    err_msg = (
        f"Audio conversion failed for '{os.path.basename(audio_path)}'. "
        f"Details: {'; '.join(conversion_errors)}. "
        "Please provide audio in standard 16-bit PCM WAV format or install ffmpeg."
    )
    logger.error(f"[Audio] {err_msg}")
    return None, err_msg


# ── Sentiment Formatting Helpers ─────────────────────────────────────────────

def format_vocal_sentiment(sentiment: dict) -> str:
    """Formats the acoustic tone and sentiment extracted from spoken audio."""
    if not isinstance(sentiment, dict):
        return f"🎙️ Vocal Sentiment: {sentiment}"

    query_sentiment = sentiment.get("query_sentiment", "neutral").capitalize()
    tone = sentiment.get("tone", "objective and formal")
    confidence = sentiment.get("confidence", 0.90)
    score = sentiment.get("sentiment_score", 0.0)

    return (
        f"🎙️ Detected Spoken Query Acoustics:\n"
        f"• Sentiment: {query_sentiment} (valence score: {score:+.2f})\n"
        f"• Vocal Tone: {tone}\n"
        f"• Acoustic Confidence: {confidence:.0%}"
    )


def analyze_text_sentiment(text: str) -> str:
    """Keyword-based sentiment analysis for typed text queries."""
    positive_words = {"great", "excellent", "good", "positive", "success", "helpful", "accurate", "clear", "optimal"}
    negative_words = {"bad", "poor", "error", "fail", "negative", "wrong", "issue", "problem", "missed", "breach"}
    words = set(text.lower().split())
    pos = len(words & positive_words)
    neg = len(words & negative_words)
    if pos > neg:
        return f"⌨️ Text Sentiment: Positive (score: +{pos})"
    elif neg > pos:
        return f"⌨️ Text Sentiment: Negative (score: -{neg})"
    return "⌨️ Text Sentiment: Neutral / Informational"


# ── Mock Response Generators (Clearly Labeled as MOCK) ───────────────────────

def _mock_summarize(text: str) -> str:
    words = text.split()[:75]
    return (
        "🔴 [MOCK SUMMARY]\n"
        f"Document excerpt: \"{' '.join(words)}...\"\n\n"
        "(Running in MOCK mode — configure GEMINI_API_KEY in Space Settings → Secrets for live executive summary)."
    )


def _mock_audio_answer(summary: str, audio_path: str) -> Tuple[str, str]:
    """Honest mock response when audio input is provided without an API key."""
    filename = os.path.basename(audio_path)
    answer = (
        "🔴 [MOCK DEMO RESPONSE — AUDIO QUERY RECEIVED]\n\n"
        f"Microphone audio recording '{filename}' was successfully captured and validated as 16-bit PCM WAV.\n\n"
        "However, GEMINI_API_KEY is not configured on this Space. In LIVE mode, Gemini 3.5 Flash-Lite "
        "processes your spoken WAV audio natively alongside the document text to extract exact metrics, "
        "numerical thresholds, and document-grounded answers without speech-to-text error cascades.\n\n"
        "👉 To enable live Gemini spoken QA and acoustic tone extraction, configure GEMINI_API_KEY "
        "in Hugging Face Space Settings → Secrets."
    )
    sentiment = (
        "🔴 [MOCK DEMO — SIMULATED VOCAL TONE]\n"
        "• Spoken Sentiment: Inquisitive (Mock Demo)\n"
        "• Vocal Tone: Inquisitive / Spoken Question (Simulated)\n"
        "• Note: Configure GEMINI_API_KEY for live acoustic tone extraction."
    )
    return answer, sentiment


def _mock_text_answer(summary: str, question: str) -> Tuple[str, str]:
    """Mock response for typed text queries."""
    answer = (
        f"🔴 [MOCK DEMO RESPONSE]\n\n"
        f"Mock answer for '{question}': Based on the document, this is a simulated response. "
        "Configure GEMINI_API_KEY in Space Settings → Secrets for live Gemini-powered answers."
    )
    sentiment = analyze_text_sentiment(question)
    return answer, sentiment


# ── Main Gradio Event Handler ────────────────────────────────────────────────

def process_document_and_query(pdf_file, audio_file, text_question: str):
    """
    Unified Gradio handler supporting PDF upload and dual audio/text inputs.
    Voice audio input takes precedence over typed text if both are supplied.
    """
    if pdf_file is None:
        return (
            "⚠️ Please upload a PDF document first.",
            "Upload a PDF and ask a question using either the microphone or text box.",
            ""
        )

    has_audio = audio_file is not None and bool(str(audio_file).strip())
    has_text = bool(text_question) and bool(text_question.strip())

    if not has_audio and not has_text:
        return (
            "PDF document uploaded successfully. Please ask a question.",
            "⚠️ Please ask a question by recording with your microphone (🎙️) or typing in the text box (⌨️).",
            ""
        )

    # Extract text from PDF
    pdf_path = pdf_file.name if hasattr(pdf_file, "name") else str(pdf_file)

    try:
        if MOCK_MODE:
            import fitz
            doc = fitz.open(pdf_path)
            raw_text = "".join(p.get_text() for p in doc)
            if not raw_text.strip():
                raw_text = "Empty or image-only PDF document."
            summary = _mock_summarize(raw_text)
        else:
            raw_text = extract_text_from_pdf(pdf_path)
            summary = summarize_book(raw_text)
    except Exception as pdf_err:
        logger.error(f"Error extracting PDF: {pdf_err}", exc_info=True)
        return f"❌ PDF Extraction Error: {pdf_err}", "", ""

    # Route query: Audio takes precedence over text
    if has_audio:
        logger.info(f"Routing to AUDIO pipeline with file: {audio_file}")
        wav_path, conv_err = prepare_audio_for_gemini(audio_file)
        if conv_err:
            return summary, f"❌ Audio Processing Error: {conv_err}", "Audio validation failed"

        if MOCK_MODE:
            answer, sentiment = _mock_audio_answer(summary, wav_path)
            return summary, answer, sentiment
        else:
            # LIVE Gemini Multimodal Audio Pipeline
            try:
                answer, sentiment_dict = process_query_with_llm(
                    document_context=raw_text,
                    audio_path=wav_path,
                    book_summary=summary
                )
                sentiment = format_vocal_sentiment(sentiment_dict)
                return summary, answer, sentiment
            except Exception as e:
                logger.error(f"Live audio processing error: {e}", exc_info=True)
                return summary, f"❌ Gemini Live Audio Error: {e}", "Error extracting vocal acoustics"
    else:
        logger.info(f"Routing to TEXT pipeline with question: {text_question[:60]}")
        if MOCK_MODE:
            answer, sentiment = _mock_text_answer(summary, text_question)
            return summary, answer, sentiment
        else:
            # LIVE Gemini Text Pipeline
            try:
                import google.generativeai as genai
                model = genai.GenerativeModel(GEMINI_MODEL)
                truncated_context = raw_text[:MAX_DOCUMENT_CHARS]
                prompt = (
                    "Based on the following document, answer the question accurately "
                    "with exact metrics, bounds, and requirements:\n\n"
                    f"{truncated_context}\n\nQuestion: {text_question}"
                )
                resp = model.generate_content([{"text": prompt}])
                answer = resp.text
                sentiment = analyze_text_sentiment(answer)
                return summary, answer, sentiment
            except Exception as e:
                logger.error(f"Live text processing error: {e}", exc_info=True)
                return summary, f"❌ Gemini Live Text Error: {e}", "Error processing text question"


# ── Gradio User Interface ───────────────────────────────────────────────────

MODE_BADGE = "🔴 MOCK DEMO (No API Key)" if MOCK_MODE else "🟢 LIVE (Gemini Connected)"

if MOCK_MODE:
    MODE_BANNER_HTML = """
    <div style="background-color: #fff3f3; border: 2px solid #e53935; border-radius: 8px; padding: 12px 18px; margin: 12px 0;">
        <h3 style="color: #c62828; margin: 0 0 6px 0; font-size: 1.15em;">🔴 MOCK DEMO MODE — No API Key Configured</h3>
        <p style="margin: 0; color: #424242; font-size: 0.95em;">
            Responses are <b>simulated demonstrations</b>. To enable live Gemini multimodal speech-to-text,
            document QA, and acoustic tone analysis, configure <code>GEMINI_API_KEY</code> in Space <b>Settings &rarr; Secrets</b>.
        </p>
    </div>
    """
else:
    MODE_BANNER_HTML = """
    <div style="background-color: #f1f8e9; border: 2px solid #43a047; border-radius: 8px; padding: 12px 18px; margin: 12px 0;">
        <h3 style="color: #2e7d32; margin: 0 0 6px 0; font-size: 1.15em;">🟢 LIVE MODE — Gemini Multimodal Connected</h3>
        <p style="margin: 0; color: #424242; font-size: 0.95em;">
            <b>Gemini 3.5 Flash-Lite</b> is connected. Microphone audio and PDF document text are ingested
            natively with exact document grounding and acoustic vocal tone extraction.
        </p>
    </div>
    """

with gr.Blocks(title="Speech-to-Text & Document Intelligence API Demo") as demo:
    gr.Markdown(f"""
    # 🎙️ Speech-to-Text & Document Intelligence API
    **Interactive Multimodal Demo** | {MODE_BADGE}
    """)
    gr.HTML(MODE_BANNER_HTML)
    gr.Markdown("""
    Upload a technical PDF document, then **ask your question by voice** (using your microphone) or by typing.
    In **LIVE** mode, Gemini ingests raw spoken audio natively to provide document-grounded answers and detect your vocal tone/emotion.

    > **Repository Source**: [HiteshReddy2002/speech-and-text-conversion-sentimentanalysis-api](https://github.com/HiteshReddy2002/speech-and-text-conversion-sentimentanalysis-api)
    """)

    with gr.Row():
        with gr.Column(scale=1):
            pdf_input = gr.File(
                label="📄 1. Upload PDF Document",
                file_types=[".pdf"],
                type="filepath"
            )

            gr.Markdown("### 2. Ask Your Question")
            audio_input = gr.Audio(
                sources=["microphone", "upload"],
                type="filepath",
                label="🎙️ Ask by voice (microphone)"
            )
            question_input = gr.Textbox(
                label="⌨️ Or type your question",
                placeholder="e.g. What is the sustained ingestion SLA for raw transactional events?",
                lines=2
            )
            gr.Markdown("*(If both voice audio and typed text are provided, voice takes precedence)*")

            submit_btn = gr.Button("🔍 Ask Question", variant="primary", size="lg")

        with gr.Column(scale=1):
            summary_output = gr.Textbox(
                label="📋 Document Executive Summary",
                lines=5,
                interactive=False
            )
            answer_output = gr.Textbox(
                label="💡 Grounded Answer",
                lines=6,
                interactive=False
            )
            sentiment_output = gr.Textbox(
                label="🎭 Vocal Tone & Sentiment Analysis",
                lines=4,
                interactive=False
            )

    submit_btn.click(
        fn=process_document_and_query,
        inputs=[pdf_input, audio_input, question_input],
        outputs=[summary_output, answer_output, sentiment_output],
    )

    gr.Examples(
        examples=[
            ["What is the sustained ingestion SLA for raw transactional events captured from Kafka?"],
            ["What are the key numerical metrics, SLAs, and thresholds in this document?"],
            ["Summarize the executive takeaways and compliance requirements."],
        ],
        inputs=[question_input],
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
