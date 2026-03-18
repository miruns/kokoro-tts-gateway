import os

API_KEY: str = os.environ.get("API_KEY", "")
MODEL_DIR: str = os.environ.get("MODEL_DIR", "/app/models")
MODEL_FILE: str = os.environ.get("MODEL_FILE", "kokoro-v0_19.onnx")
VOICES_FILE: str = os.environ.get("VOICES_FILE", "voices.bin")
DEFAULT_VOICE: str = os.environ.get("DEFAULT_VOICE", "af_heart")
