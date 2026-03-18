FROM python:3.12-slim-bookworm

# ── system dependencies ─────────────────────────────────────────────
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        espeak-ng libespeak-ng1 ffmpeg curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── python dependencies ─────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── download model weights at build time ─────────────────────────────
# Override these build-args if the upstream repo or filenames change.
ARG HF_REPO=hexgrad/Kokoro-82M-ONNX
ARG MODEL_FILE=kokoro-v0_19.onnx
ARG VOICES_FILE=voices.bin

RUN python -c "\
from huggingface_hub import hf_hub_download; \
hf_hub_download('${HF_REPO}', '${MODEL_FILE}', local_dir='/app/models'); \
hf_hub_download('${HF_REPO}', '${VOICES_FILE}', local_dir='/app/models'); \
print('Models downloaded successfully')"

# ── application ──────────────────────────────────────────────────────
COPY app/ app/

ENV MODEL_DIR=/app/models
ENV MODEL_FILE=${MODEL_FILE}
ENV VOICES_FILE=${VOICES_FILE}

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
