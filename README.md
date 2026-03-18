# Kokoro TTS Gateway

Lightweight REST API that serves the **Kokoro-82M** text-to-speech model over HTTP with streaming audio responses. Built with FastAPI, powered by ONNX Runtime, and optimized for low-cost scale to 0 Fly.io deployment.

## Features

- **Streaming WAV output** — playback begins before the full utterance is generated
- **Single model load** — the ONNX model is loaded once at startup, not per-request
- **API-key auth** — global `X-API-Key` header validation (except `/health`)
- **Fly.io-ready** — `fly.toml` with auto-start/stop, low concurrency, and shared-CPU VMs
- **Docker build caches model weights** — container starts instantly with no runtime downloads

## Project Structure

```
app/
├── main.py      # FastAPI application + lifespan hook
├── config.py    # Environment-driven settings
├── auth.py      # API key middleware
├── routes.py    # /health and /tts endpoints
└── tts.py       # Kokoro ONNX inference + WAV streaming
Dockerfile
fly.toml
requirements.txt
```

## Quickstart (local)

```bash
# 1. Create a virtual environment
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download model files
python -c "
from huggingface_hub import hf_hub_download
hf_hub_download('hexgrad/Kokoro-82M-ONNX', 'kokoro-v0_19.onnx', local_dir='models')
hf_hub_download('hexgrad/Kokoro-82M-ONNX', 'voices.bin', local_dir='models')
"

# 4. Ensure espeak-ng is installed
#    Ubuntu/Debian: sudo apt install espeak-ng
#    macOS:         brew install espeak-ng
#    Windows:       https://github.com/espeak-ng/espeak-ng/releases

# 5. Run the server
API_KEY=my-secret MODEL_DIR=models uvicorn app.main:app --reload
```

## API

### `GET /health`

Public health-check endpoint (no auth required).

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### `POST /tts`

Generate speech from text. Returns streaming `audio/wav`.

| Field   | Type   | Required | Default     | Constraints          |
|---------|--------|----------|-------------|----------------------|
| `text`  | string | yes      | —           | 1 – 2 000 chars      |
| `voice` | string | no       | `af_heart`  | any Kokoro voice ID  |
| `speed` | float  | no       | `1.0`       | 0.5 – 2.0           |

```bash
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -H "X-API-Key: my-secret" \
  -d '{"text": "Hello from Kokoro!"}' \
  --output speech.wav
```

### Available Voices

| Voice ID      | Description        |
|---------------|--------------------|
| `af_heart`    | American Female    |
| `af_bella`    | American Female    |
| `af_sarah`    | American Female    |
| `am_adam`     | American Male      |
| `am_michael`  | American Male      |
| `bf_emma`     | British Female     |
| `bm_george`   | British Male       |

See the Kokoro model card for the full list.

## Environment Variables

| Variable        | Default                | Description                        |
|-----------------|------------------------|------------------------------------|
| `API_KEY`       | *(empty — all denied)* | Secret key for `X-API-Key` header  |
| `MODEL_DIR`     | `/app/models`          | Directory containing model files   |
| `MODEL_FILE`    | `kokoro-v0_19.onnx`    | ONNX model filename               |
| `VOICES_FILE`   | `voices.bin`           | Voice embeddings filename          |
| `DEFAULT_VOICE` | `af_heart`             | Default voice when none specified  |

## Docker

```bash
docker build -t kokoro-tts-gateway .
docker run -p 8000:8000 -e API_KEY=my-secret kokoro-tts-gateway
```

Model weights are downloaded during `docker build` so the container starts without network fetches.

To use a different model repo or filenames:

```bash
docker build \
  --build-arg HF_REPO=hexgrad/Kokoro-82M-ONNX \
  --build-arg MODEL_FILE=kokoro-v0_19.onnx \
  --build-arg VOICES_FILE=voices.bin \
  -t kokoro-tts-gateway .
```

## Deploy to Fly.io

```bash
# 1. Install flyctl and authenticate
fly auth login

# 2. Create the app (edit fly.toml app name first)
fly apps create kokoro-tts-gateway

# 3. Set the API key secret
fly secrets set API_KEY=my-secret

# 4. Deploy
fly deploy

# 5. Verify
curl https://kokoro-tts-gateway.fly.dev/health
```

The `fly.toml` is pre-configured with:
- Shared CPU, 1 GB RAM
- `min_machines_running = 0` — scales to zero when idle
- `auto_stop_machines = "stop"` / `auto_start_machines = true`
- `hard_limit = 2` concurrent requests (TTS is CPU-intensive)
- Health check on `/health`

## License

[MIT](LICENSE)
