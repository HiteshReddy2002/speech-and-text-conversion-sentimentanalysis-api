"""
Native Audio Arm for Document-Grounded Spoken QA Evaluation Harness.
Interface: input (pdf_id, question_id, wav_path) -> output (answer, stage_latencies, tokens_used)

Executes the native multimodal audio pipeline:
WAV audio bytes -> Gemini inline_data + full document context -> answer.
"""

import os
import sys
import time
import json
import logging
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv
load_dotenv(REPO_ROOT / ".env")

import main
import google.generativeai as genai

logger = logging.getLogger(__name__)


class ArmResult(dict):
    """
    Standardized result object matching both dictionary and tuple unpacking interfaces:
    answer, stage_latencies, tokens_used = result
    """
    def __init__(
        self,
        answer: str,
        stage_latencies: dict,
        tokens_used: dict,
        transcript: str = "",
        arm: str = "native",
        pdf_id: str = "",
        question_id: str = "",
        raw_response: str = "",
        sentiment: dict = None,
        **kwargs
    ):
        super().__init__(
            answer=answer,
            stage_latencies=stage_latencies,
            tokens_used=tokens_used,
            transcript=transcript,
            arm=arm,
            pdf_id=pdf_id,
            question_id=question_id,
            raw_response=raw_response,
            sentiment=sentiment or {},
            **kwargs
        )
        self.answer = answer
        self.stage_latencies = stage_latencies
        self.tokens_used = tokens_used
        self.transcript = transcript
        self.arm = arm
        self.pdf_id = pdf_id
        self.question_id = question_id
        self.raw_response = raw_response
        self.sentiment = sentiment or {}

    def __iter__(self):
        """Allows unpacking: answer, stage_latencies, tokens_used = result"""
        return iter((self.answer, self.stage_latencies, self.tokens_used))


def call_with_retry(fn, *args, max_retries=10, delay=8, **kwargs):
    """Executes API call with exponential backoff on rate limits."""
    for attempt in range(max_retries):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            err_str = str(e).lower()
            if "resource_exhausted" in err_str or "429" in err_str or "quota" in err_str:
                wait_time = min(90, delay * (attempt + 1))
                logger.warning(
                    f"[Native Arm] Rate limited (attempt {attempt+1}/{max_retries}). "
                    f"Backing off for {wait_time}s..."
                )
                time.sleep(wait_time)
            else:
                logger.error(f"[Native Arm] API call error: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(delay)
    raise RuntimeError("[Native Arm] Max retries exceeded.")


def resolve_pdf_path(pdf_id: str | Path, data_dir: Path = None) -> Path:
    """Resolves pdf_id to a concrete Path."""
    p = Path(pdf_id)
    if p.exists() and p.is_file():
        return p
    if data_dir is None:
        data_dir = REPO_ROOT / "eval" / "data"
    candidate = data_dir / p.name
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"Cannot find PDF for identifier: {pdf_id} (searched {candidate})")


def run_native_arm(
    pdf_id: str | Path,
    question_id: str,
    wav_path: str | Path,
    data_dir: Path = None,
    model_name: str = None
) -> ArmResult:
    """
    Executes Native Audio Arm.
    Input: (pdf_id, question_id, wav_path)
    Output: ArmResult (answer, stage_latencies, tokens_used)
    """
    pdf_path = resolve_pdf_path(pdf_id, data_dir)
    wav_path = Path(wav_path)
    if not wav_path.exists():
        raise FileNotFoundError(f"Audio file not found: {wav_path}")

    # Stage 0: Context extraction / cache retrieval (refactored full document logic)
    document_context = main.get_cached_or_extracted_text(str(pdf_path))
    context_str = f"=== DOCUMENT CONTENT ===\n{document_context[:main.MAX_DOCUMENT_CHARS]}\n"

    # Read binary audio data for inline_data
    with open(wav_path, "rb") as f:
        audio_bytes = f.read()

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

    effective_model = model_name or main.GEMINI_MODEL
    model = genai.GenerativeModel(effective_model)

    # Stage 1: Multimodal LLM inference
    t0 = time.perf_counter()
    response = call_with_retry(
        model.generate_content,
        [
            {"text": system_prompt},
            {"text": context_str},
            {
                "inline_data": {
                    "mime_type": "audio/wav",
                    "data": audio_bytes
                }
            }
        ]
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

    sentiment = {}
    try:
        parsed = json.loads(cleaned)
        answer = parsed.get("answer", raw_response)
        sentiment = parsed.get("sentiment", {})
    except Exception:
        logger.warning(f"Could not parse native response as JSON for [{question_id}]. Using raw text.")
        answer = raw_response

    # Stage Latencies
    stage_latencies = {
        "stt": 0.0,
        "llm": round(t_llm, 3),
        "tts": 0.0,
        "total": round(t_llm, 3)
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
        transcript="",
        arm="native",
        pdf_id=str(Path(pdf_id).name),
        question_id=question_id,
        raw_response=raw_response,
        sentiment=sentiment
    )


# Standard interface alias
run = run_native_arm


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run Native Audio Arm on single question")
    parser.add_argument("--pdf", required=True, help="PDF filename or path")
    parser.add_argument("--qid", required=True, help="Question ID")
    parser.add_argument("--wav", required=True, help="Path to WAV audio file")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    ans, lat, tok = run(args.pdf, args.qid, args.wav)
    print(f"\n[Native Arm Output - {args.qid}]")
    print(f"Answer: {ans}")
    print(f"Latencies: {lat}")
    print(f"Tokens: {tok}")
