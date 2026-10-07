"""
Cascaded Pipeline Arm for Document-Grounded Spoken QA Evaluation Harness.
Interface: input (pdf_id, question_id, wav_path) -> output (answer, stage_latencies, tokens_used)

Executes the cascaded pipeline:
1. Speech-to-Text: Locally transcribe WAV audio using faster-whisper on CPU (no audio leaves machine).
2. Text LLM: Full document context (reused refactor logic) + transcript -> Gemini text model -> answer.
3. Text-to-Speech: Skipped (consistent with evaluation benchmark environment).
"""

import os
import sys
import time
import wave
import json
import logging
from pathlib import Path
from typing import Optional
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv
load_dotenv(REPO_ROOT / ".env")

import main
import google.generativeai as genai
from faster_whisper import WhisperModel

# Import ArmResult and helpers from native_arm for interface parity
from eval.native_arm import ArmResult, resolve_pdf_path, call_with_retry

logger = logging.getLogger(__name__)

# Global cached WhisperModel instance to avoid reload overhead per item
_CACHED_WHISPER_MODEL: Optional[WhisperModel] = None
_CACHED_MODEL_SIZE: Optional[str] = None


def get_whisper_model(model_size: str = "base", device: str = "cpu", compute_type: str = "int8") -> WhisperModel:
    """Returns a cached, locally-loaded faster-whisper model on CPU."""
    global _CACHED_WHISPER_MODEL, _CACHED_MODEL_SIZE
    if _CACHED_WHISPER_MODEL is None or _CACHED_MODEL_SIZE != model_size:
        logger.info(f"[Cascade Arm] Loading local faster-whisper model '{model_size}' on {device} ({compute_type})...")
        _CACHED_WHISPER_MODEL = WhisperModel(model_size, device=device, compute_type=compute_type)
        _CACHED_MODEL_SIZE = model_size
        logger.info(f"[Cascade Arm] Whisper model '{model_size}' loaded successfully.")
    return _CACHED_WHISPER_MODEL


def load_audio_16k(wav_path: str | Path) -> np.ndarray:
    """
    Decodes standard PCM WAV files into a 16kHz mono float32 NumPy array.
    Using Python's standard wave library avoids PyAV version compatibility issues
    and guarantees zero network I/O.
    """
    with wave.open(str(wav_path), "rb") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        raw_bytes = wf.readframes(n_frames)

    if sampwidth == 2:
        audio = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    elif sampwidth == 4:
        audio = np.frombuffer(raw_bytes, dtype=np.int32).astype(np.float32) / 2147483648.0
    elif sampwidth == 1:
        audio = (np.frombuffer(raw_bytes, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
    else:
        raise ValueError(f"Unsupported WAV sample width: {sampwidth}")

    if n_channels > 1:
        audio = audio.reshape(-1, n_channels).mean(axis=1)

    target_rate = 16000
    if framerate != target_rate:
        target_len = int(len(audio) * target_rate / framerate)
        audio = np.interp(
            np.linspace(0, len(audio), target_len, endpoint=False),
            np.arange(len(audio)),
            audio
        ).astype(np.float32)

    return audio


def transcribe_locally(wav_path: str | Path, whisper_model: WhisperModel = None, model_size: str = "base") -> tuple[str, float]:
    """
    Transcribes audio strictly locally on CPU.
    Returns: (transcript: str, latency_sec: float)
    """
    model = whisper_model or get_whisper_model(model_size=model_size)
    audio_data = load_audio_16k(wav_path)

    t0 = time.perf_counter()
    segments, _ = model.transcribe(audio_data, beam_size=5, language="en")
    transcript = " ".join(s.text.strip() for s in segments).strip()
    t_stt = time.perf_counter() - t0

    return transcript, t_stt


def run_cascade_arm(
    pdf_id: str | Path,
    question_id: str,
    wav_path: str | Path,
    data_dir: Path = None,
    model_name: str = None,
    whisper_model_size: str = "base"
) -> ArmResult:
    """
    Executes Cascaded STT -> Text LLM -> TTS Arm.
    Input: (pdf_id, question_id, wav_path)
    Output: ArmResult (answer, stage_latencies, tokens_used)
    """
    pdf_path = resolve_pdf_path(pdf_id, data_dir)
    wav_path = Path(wav_path)
    if not wav_path.exists():
        raise FileNotFoundError(f"Audio file not found: {wav_path}")

    # Stage 1: Local Speech-to-Text via faster-whisper on CPU
    logger.info(f"[Cascade Arm] Transcribing {wav_path.name} locally with faster-whisper ({whisper_model_size})...")
    transcript, t_stt = transcribe_locally(wav_path, model_size=whisper_model_size)
    logger.info(f"[Cascade Arm] Transcribed [{question_id}] in {t_stt:.3f}s: \"{transcript}\"")

    # Stage 0: Context extraction / cache retrieval (refactored full document logic)
    document_context = main.get_cached_or_extracted_text(str(pdf_path))
    context_str = f"=== DOCUMENT CONTENT ===\n{document_context[:main.MAX_DOCUMENT_CHARS]}\n"

    system_prompt = """
You are an expert, precise document intelligence assistant.
Answer the user's question based STRICTLY on the provided document content.

Rules for your answer:
1. Provide exact numbers, metrics, upper/lower bounds, dates, and specifications when present in the document.
2. If the document does not contain the answer or the information is not provided, state clearly and concisely that the document does not mention it. Do not invent or extrapolate facts not in the text.

Respond ONLY with valid JSON in this exact structure:
{
  "answer": "<direct, exact answer to the user's question>"
}
"""

    effective_model = model_name or main.GEMINI_MODEL
    model = genai.GenerativeModel(effective_model)

    user_query_str = f"=== USER QUESTION (TRANSCRIBED FROM AUDIO) ===\n{transcript}\n"

    # Stage 2: Text LLM inference
    t0 = time.perf_counter()
    response = call_with_retry(
        model.generate_content,
        [
            {"text": system_prompt},
            {"text": context_str},
            {"text": user_query_str}
        ],
        request_options={"timeout": 90.0}
    )
    t_llm = time.perf_counter() - t0

    # Parse response
    raw_response = response.text.strip()
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
    except Exception:
        logger.warning(f"Could not parse cascade response as JSON for [{question_id}]. Using raw text.")
        answer = raw_response

    # Stage Latencies
    stage_latencies = {
        "stt": round(t_stt, 3),
        "llm": round(t_llm, 3),
        "tts": 0.0,
        "total": round(t_stt + t_llm, 3)
    }

    # Token Usage
    usage = getattr(response, "usage_metadata", None)
    prompt_tokens = getattr(usage, "prompt_token_count", 0) if usage else 0
    candidates_tokens = getattr(usage, "candidates_token_count", 0) if usage else 0
    total_tokens = getattr(usage, "total_token_count", 0) if usage else (prompt_tokens + candidates_tokens)

    tokens_used = {
        "prompt_tokens": prompt_tokens,
        "candidates_tokens": candidates_tokens,
        "total_tokens": total_tokens
    }

    return ArmResult(
        answer=answer,
        stage_latencies=stage_latencies,
        tokens_used=tokens_used,
        transcript=transcript,
        arm="cascade",
        pdf_id=str(Path(pdf_id).name),
        question_id=question_id,
        raw_response=raw_response
    )


# Standard interface alias
run = run_cascade_arm


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run Cascade Arm on single question")
    parser.add_argument("--pdf", required=True, help="PDF filename or path")
    parser.add_argument("--qid", required=True, help="Question ID")
    parser.add_argument("--wav", required=True, help="Path to WAV audio file")
    parser.add_argument("--whisper-size", default="base", help="Whisper model size (default: base)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    res = run(args.pdf, args.qid, args.wav, whisper_model_size=args.whisper_size)
    print(f"\n[Cascade Arm Output - {args.qid}]")
    print(f"Transcript: {res.transcript}")
    print(f"Answer: {res.answer}")
    print(f"Latencies: {res.stage_latencies}")
    print(f"Tokens: {res.tokens_used}")
