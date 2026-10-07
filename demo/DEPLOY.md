# Deploy to Hugging Face Spaces

This guide deploys the Speech & Sentiment API demo to [Hugging Face Spaces](https://huggingface.co/spaces) using Gradio SDK.

## Prerequisites

- [Hugging Face account](https://huggingface.co/join)
- `huggingface_hub` CLI: `pip install huggingface_hub`
- A Gemini API key ([get one here](https://aistudio.google.com/app/apikey))

---

## Steps

### 1. Authenticate with Hugging Face & Create Space

Run the CLI login:
```bash
huggingface-cli login
```
When prompted for your token:
```text
Token: <PASTE_YOUR_HUGGING_FACE_WRITE_TOKEN_HERE (hf_...)>
```
(Generate your token at https://huggingface.co/settings/tokens with Write permissions).

Then create the Gradio Space:
```bash
huggingface-cli repo create speech-sentiment-demo --type space --space_sdk gradio
```

### 2. Clone the Space repo

```bash
git clone https://huggingface.co/spaces/hitesh125/speech-sentiment-demo
cd speech-sentiment-demo
```

### 3. Copy demo files

```bash
# From within the speech-and-text-conversion-sentimentanalysis-api repo root:
cp demo/app.py ../speech-sentiment-demo/app.py
cp demo/requirements-demo.txt ../speech-sentiment-demo/requirements.txt
# Also copy main.py (the demo imports helpers from it)
cp main.py ../speech-sentiment-demo/main.py
```

### 4. Add secrets (Hugging Face Space Secrets)

In your Space settings (Settings → Secrets), add:

| Secret Name | Value |
|-------------|-------|
| `GEMINI_API_KEY` | Your Gemini API key |

> **Do NOT** hardcode secrets in any file. The demo reads from env vars automatically.

### 5. Push to Spaces

```bash
cd ../speech-sentiment-demo
git add .
git commit -m "Initial deploy: Speech & Sentiment Gradio demo"
git push
```

### 6. Monitor & Verify

- Build logs are visible in the Space's **Logs** tab.
- The live Space URL is: `https://huggingface.co/spaces/hitesh125/mini-chatbot` (Embed domain: `https://hitesh125-mini-chatbot.hf.space`)
- Default repository target: `https://huggingface.co/spaces/hitesh125/speech-sentiment-demo`

#### Verification Checklist:
1. **Configure Secret:** In Space **Settings → Secrets**, ensure `GEMINI_API_KEY` is added.
2. **Redeploy / Restart Space:** Click **Factory rebuild** or restart the Space to load the secret.
3. **Voice Audio Test:** Upload a technical PDF, click the microphone button under **🎙️ Ask by voice (microphone)**, speak your question, and click **Ask Question**.
4. **Inspect Readout:** Verify that:
   - The banner indicates `🟢 LIVE MODE — Gemini Multimodal Connected`.
   - The document summary and grounded answer are displayed.
   - The **🎭 Vocal Tone & Sentiment Analysis** box displays the acoustic tone and sentiment breakdown extracted from the audio query.

---

## Notes

- Without `GEMINI_API_KEY`, the demo runs in **mock mode** and shows an unmissable red banner with simulated mock responses.
- For GCP Text-to-Speech (audio response synthesis), upload your service account JSON as a secret — see [HF Secrets docs](https://huggingface.co/docs/hub/spaces-overview#managing-secrets).
- Free Spaces use CPU-only instances (2 vCPU, 16 GB RAM) — fully sufficient for this Gradio demo.
