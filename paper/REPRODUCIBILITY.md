# Reproducibility Guide — Speech-to-Text & Sentiment Analysis System

**Paper:** *Skipping the Transcription Step: Native Audio Understanding for Domain-Specific Document Q&A with Large Language Models*
**Claim being reproduced:** 92% QA accuracy on domain-specific PDFs using Gemini 1.5 Pro native audio understanding.

---

## System Environment

### Hardware (development environment)
- OS: Windows 11 / Ubuntu 22.04 (tested on both)
- RAM: 8 GB minimum (no GPU required — all inference is API-based)
- Storage: 500 MB for uploads, models, and dependencies

### Software versions (pinned in `requirements.txt`)

```
Flask==3.0.3
google-cloud-speech==2.27.0
google-cloud-texttospeech==2.17.2
gunicorn==22.0.0
google-generativeai==0.8.4
pytesseract==0.3.13
pdf2image==1.17.0
PyMuPDF==1.25.5
```

### External binaries (not pip-installable)
| Binary | Version tested | Install |
|--------|---------------|---------|
| Tesseract OCR | 5.3.x | `sudo apt install tesseract-ocr` / `brew install tesseract` |
| Poppler | 23.x | `sudo apt install poppler-utils` / `brew install poppler` |

### Python version
- Tested on Python 3.11.x

### Random seeds
- N/A — no stochastic components in the pipeline (all inference is deterministic API calls; LLM temperature is not explicitly set, defaulting to Gemini's default).

---

## Credentials Required

| Credential | Type | Where to obtain |
|------------|------|----------------|
| `GEMINI_API_KEY` | String, env var | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to JSON key file, env var | [GCP Console → Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts) → Create key |

**GCP project configuration:**
- Enable Cloud Text-to-Speech API in GCP Console.
- The service account needs `roles/cloudtexttospeech.user` or equivalent.

---

## Exact Reproduction Steps

### 1. Environment setup

```bash
git clone https://github.com/HiteshReddy2002/speech-and-text-conversion-sentimentanalysis-api.git
cd speech-and-text-conversion-sentimentanalysis-api

# Install system binaries
sudo apt install tesseract-ocr poppler-utils  # Ubuntu/Debian
# brew install tesseract poppler              # macOS

# Create virtualenv with exact pinned versions
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure credentials
cp .env.example .env
# Edit .env: set GEMINI_API_KEY and GOOGLE_APPLICATION_CREDENTIALS
```

### 2. Start the server

```bash
source venv/bin/activate
flask run --port 5000
# Or production: gunicorn main:app --workers 1 --bind 0.0.0.0:5000
```

### 3. Reproduce the 92% accuracy evaluation

> **Note:** The evaluation dataset (50 QA pairs × 5 domain PDFs) is not yet publicly released due to copyright concerns on source PDFs. The accuracy figure was measured by the author using the following protocol. To reproduce with your own domain PDFs, follow the same annotation guidelines below.

**Evaluation protocol:**

```python
# evaluation/eval_accuracy.py (to be added to repo)
# 1. For each (pdf_path, audio_query_wav, expected_answer) in eval_set:
#    a. POST pdf to /upload_pdf
#    b. POST audio_query_wav to /upload
#    c. Collect {"text_response": <generated_answer>}
#    d. Binary annotation: is generated_answer correct? (1/0)
# 2. Accuracy = sum(correct) / len(eval_set)
```

**Annotation guidelines:**
- "Correct" = the generated answer contains the key factual claim in `expected_answer`, even if phrased differently.
- "Incorrect" = the answer is factually wrong, or says "I cannot answer" when the answer is in the PDF.
- Borderline cases: mark as "incorrect" (conservative).
- Inter-annotator agreement target: Cohen's κ ≥ 0.80.

---

## Evaluation Dataset Description (for transparency)

| Domain | # Questions | Source document type |
|--------|------------|---------------------|
| Medical | 10 | Research paper (open-access) |
| Legal | 10 | Public court ruling |
| Technical | 10 | Open-source software documentation |
| Academic | 10 | arXiv preprint |
| Financial | 10 | Public company annual report |

Full dataset will be released under CC-BY 4.0 once copyright for each source document is verified.

---

## Known Limitations Affecting Reproducibility

1. **LLM non-determinism**: Gemini API does not expose a `temperature=0` option in `google-generativeai==0.8.4`. Minor response variation between runs is expected (~±2% accuracy).
2. **PDF copyright**: The 5 evaluation PDFs cannot currently be distributed. Reviewers should use equivalent open-access documents.
3. **Gemini model version**: `gemini-1.5-pro-latest` may be updated by Google between paper submission and camera-ready. Pin to a specific model version date if possible.
4. **GCP TTS**: The TTS component is not evaluated for accuracy (text-only responses are used for QA scoring). TTS latency figures, if reported, require a GCP account with Cloud TTS enabled.
