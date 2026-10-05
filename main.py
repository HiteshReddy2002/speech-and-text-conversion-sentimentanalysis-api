import os
import io
import json
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract
import google.generativeai as genai
from google.cloud import texttospeech
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'wav'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ── Gemini API Configuration ──────────────────────────────────────────────────
_GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
if not _GEMINI_KEY:
    raise EnvironmentError(
        "GEMINI_API_KEY environment variable is not set. "
        "Copy .env.example to .env and add your key before running."
    )
genai.configure(api_key=_GEMINI_KEY)

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")
MAX_DOCUMENT_CHARS = int(os.environ.get("MAX_DOCUMENT_CHARS", 50000))

# ── Google Cloud TTS Client Setup (graceful degradation) ───────────────────────
try:
    tts_client = texttospeech.TextToSpeechClient()
    logging.info("Google Cloud Text-to-Speech client initialized successfully.")
except Exception as e:
    tts_client = None
    logging.warning(f"Google Cloud Text-to-Speech client unconfigured or unavailable: {e}")


def allowed_file(filename, exts):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in exts


def extract_text_from_pdf(pdf_path):
    """Extracts text from PDF using PyMuPDF with Tesseract OCR fallback."""
    doc = fitz.open(pdf_path)
    text = ""
    for i, page in enumerate(doc):
        page_text = page.get_text()
        logging.info(f"Page {i + 1}: Extracted {len(page_text)} characters.")
        text += page_text

    if not text.strip():
        logging.warning("No selectable text found in PDF. Attempting OCR fallback...")
        try:
            images = convert_from_path(pdf_path)
            for i, img in enumerate(images):
                ocr_text = pytesseract.image_to_string(img)
                logging.info(f"OCR Page {i + 1}: Extracted {len(ocr_text)} characters.")
                text += ocr_text
        except Exception as e:
            logging.error(f"OCR fallback failed: {e}")

    logging.info(f"Final extracted text length: {len(text)} characters.")
    return text


def get_cached_or_extracted_text(pdf_path):
    """Retrieves cached document text if present, or extracts and caches it."""
    cache_path = str(pdf_path) + ".extracted.txt"
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logging.warning(f"Could not read text cache {cache_path}: {e}")

    text = extract_text_from_pdf(pdf_path)
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        logging.warning(f"Could not write text cache {cache_path}: {e}")
    return text


def summarize_book(book_text):
    """Generates an executive summary of the document text."""
    logging.info("Summarizing document...")
    if not book_text or not book_text.strip():
        logging.warning("Book text is empty.")
        return "No content extracted from the PDF to summarize."

    model = genai.GenerativeModel(GEMINI_MODEL)
    truncated_text = book_text[:MAX_DOCUMENT_CHARS]
    prompt = (
        "Provide a clear, detailed executive summary of the following document. "
        "Preserve core technical standards, key numerical metrics, SLAs, and requirements:\n\n"
        f"{truncated_text}"
    )
    response = model.generate_content(prompt)
    logging.info("Summary generated successfully.")
    return response.text


def process_query_with_llm(document_context, audio_path, book_summary=None):
    """
    Answers spoken audio query against full document context and analyzes sentiment.
    Returns: (answer_text: str, sentiment_dict: dict)
    """
    logging.info(f"Processing audio query: {audio_path}")
    with io.open(audio_path, 'rb') as audio_file:
        audio_data = audio_file.read()

    context_str = f"=== DOCUMENT CONTENT ===\n{document_context[:MAX_DOCUMENT_CHARS]}\n"
    if book_summary:
        context_str += f"\n=== DOCUMENT SUMMARY ===\n{book_summary}\n"

    system_prompt = """
You are an expert, precise document intelligence assistant.
Listen carefully to the user's spoken audio question and answer it based STRICTLY on the provided document content.

Rules for your answer:
1. Provide exact numbers, metrics, upper/lower bounds, dates, and specifications when present in the document.
2. If the document does not contain the answer or the information is not provided, state clearly and concisely that the document does not mention it. Do not invent or extrapolate facts not in the text.
3. Analyze the sentiment and emotional tone of the user's spoken audio query (e.g. neutral, inquisitive, urgent, frustrated, positive).

Respond ONLY with valid JSON in this exact structure:
{
  "answer": "<direct, exact answer to the user's question>",
  "sentiment": {
    "query_sentiment": "neutral | positive | negative | inquisitive | urgent",
    "tone": "<brief description of emotional tone, e.g., calm and formal>",
    "confidence": 0.95,
    "sentiment_score": 0.0
  }
}
"""

    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content([
        {"text": system_prompt},
        {"text": context_str},
        {
            "inline_data": {
                "mime_type": "audio/wav",
                "data": audio_data
            }
        }
    ])

    raw_response = response.text.strip()
    logging.info("Raw response generated by Gemini.")

    # Strip code block fences if present
    cleaned = raw_response
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        parsed = json.loads(cleaned)
        answer = parsed.get("answer", raw_response)
        sentiment = parsed.get("sentiment", {
            "query_sentiment": "neutral",
            "tone": "objective",
            "confidence": 0.9,
            "sentiment_score": 0.0
        })
        return answer, sentiment
    except Exception:
        # Fallback if model returned plain text rather than JSON
        logging.warning("Response was not structured JSON. Using full text as answer.")
        return raw_response, {
            "query_sentiment": "neutral",
            "tone": "objective",
            "confidence": 0.8,
            "sentiment_score": 0.0
        }


def text_to_speech(response_text):
    """
    Synthesizes response text to audio via Google Cloud Text-to-Speech.
    Returns: (audio_bytes: bytes, audio_format: str)
    """
    if tts_client is None:
        raise EnvironmentError("Google Cloud Text-to-Speech credentials are not configured.")

    input_text = texttospeech.SynthesisInput(text=response_text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    # Use LINEAR16 to generate compliant 16-bit PCM WAV audio
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )
    response = tts_client.synthesize_speech(
        request={"input": input_text, "voice": voice, "audio_config": audio_config}
    )
    return response.audio_content


@app.route('/')
def index():
    files = [f for f in os.listdir(UPLOAD_FOLDER)]
    logging.info(f"Serving index with {len(files)} uploaded files.")
    return render_template('index.html', files=files)


@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    logging.info("Received PDF upload request.")
    if 'pdf_file' not in request.files:
        logging.error("No file part in request.")
        return jsonify({"error": "No file part in request"}), 400

    file = request.files['pdf_file']
    if not file or file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if allowed_file(file.filename, {'pdf'}):
        orig_name = secure_filename(file.filename) or "document.pdf"
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"{timestamp}_{orig_name}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        logging.info(f"PDF saved as: {file_path}")

        # Pre-extract and cache text to eliminate redundant processing during audio queries
        try:
            extracted_text = get_cached_or_extracted_text(file_path)
            chars = len(extracted_text)
            logging.info(f"Pre-extracted {chars} characters for {filename}")
        except Exception as e:
            logging.warning(f"Could not pre-extract text: {e}")
            chars = 0

        return jsonify({
            "message": "PDF uploaded and indexed successfully",
            "filename": filename,
            "characters_extracted": chars
        }), 200

    logging.error("Invalid file type for PDF.")
    return jsonify({"error": "Invalid file type. Only .pdf is supported."}), 400


@app.route('/upload', methods=['POST'])
def upload_audio():
    logging.info("Received audio upload request.")
    if 'audio_data' not in request.files:
        logging.error("No audio file in request.")
        return jsonify({"error": "No audio file in request"}), 400

    file = request.files['audio_data']
    if not file or file.filename == '':
        return jsonify({"error": "No audio file selected"}), 400

    if allowed_file(file.filename, {'wav'}):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        audio_filename = f"{timestamp}.wav"
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
        file.save(audio_path)
        logging.info(f"Audio saved as: {audio_path}")

        # Find the most recent PDF
        pdf_files = sorted(
            [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.pdf')],
            key=lambda f: os.path.getmtime(os.path.join(UPLOAD_FOLDER, f)),
            reverse=True
        )
        if not pdf_files:
            logging.warning("No PDF found to process with audio.")
            return jsonify({"error": "No PDF uploaded to query. Please upload a PDF first."}), 400

        latest_pdf = os.path.join(UPLOAD_FOLDER, pdf_files[0])
        logging.info(f"Querying against latest PDF: {latest_pdf}")

        # Retrieve full extracted text (from cache or extraction)
        document_text = get_cached_or_extracted_text(latest_pdf)

        try:
            # Process query with full document context and extract sentiment
            response_text, sentiment_data = process_query_with_llm(document_text, audio_path)

            # Save response text
            response_txt_path = audio_path.replace('.wav', '.txt')
            with open(response_txt_path, 'w', encoding='utf-8') as f:
                f.write(response_text)

            # Convert response to speech with graceful fallback if credentials are absent
            tts_status = "skipped_no_credentials"
            response_wav_path = None
            if tts_client is not None:
                try:
                    audio_output = text_to_speech(response_text)
                    response_wav_path = audio_path.replace('.wav', '_response.wav')
                    with open(response_wav_path, 'wb') as out:
                        out.write(audio_output)
                    tts_status = "success"
                    logging.info(f"Response audio saved to: {response_wav_path}")
                except Exception as tts_err:
                    logging.warning(f"TTS synthesis failed: {tts_err}. Continuing with text response.")
                    tts_status = f"failed: {tts_err}"

            return jsonify({
                "text_response": response_text,
                "sentiment": sentiment_data,
                "audio_response": os.path.basename(response_wav_path) if response_wav_path else None,
                "tts_status": tts_status,
                "queried_document": os.path.basename(latest_pdf)
            }), 200

        except Exception as e:
            logging.error(f"Error processing audio query: {e}", exc_info=True)
            return jsonify({"error": f"Audio processing failed: {str(e)}"}), 500

    logging.error("Invalid audio file format.")
    return jsonify({"error": "Invalid file format. Only .wav is supported."}), 400


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    logging.info(f"Serving file: {filename}")
    return send_from_directory(app.config['UPLOAD_FOLDER'], secure_filename(filename))


if __name__ == '__main__':
    logging.info("Starting Flask app...")
    app.run(debug=True)
