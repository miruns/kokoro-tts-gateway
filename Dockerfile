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
# Downloaded from https://github.com/thewh1teagle/kokoro-onnx/releases
# Override filenames with build-args (e.g. kokoro-v1.0.int8.onnx for 88 MB).
ARG RELEASE_TAG=model-files-v1.0
ARG MODEL_FILE=kokoro-v1.0.onnx
ARG VOICES_FILE=voices-v1.0.bin

RUN mkdir -p /app/models && \
    curl -fSL -o /app/models/${MODEL_FILE} \
      "https://github.com/thewh1teagle/kokoro-onnx/releases/download/${RELEASE_TAG}/${MODEL_FILE}" && \
    curl -fSL -o /app/models/${VOICES_FILE} \
      "https://github.com/thewh1teagle/kokoro-onnx/releases/download/${RELEASE_TAG}/${VOICES_FILE}" && \
    echo "Models downloaded successfully"

# ── application ──────────────────────────────────────────────────────
COPY app/ app/

ENV MODEL_DIR=/app/models
ENV MODEL_FILE=${MODEL_FILE}
ENV VOICES_FILE=${VOICES_FILE}

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
