import os

API_KEY: str = os.environ.get("API_KEY", "")
MODEL_DIR: str = os.environ.get("MODEL_DIR", "/app/models")
MODEL_FILE: str = os.environ.get("MODEL_FILE", "kokoro-v1.0.onnx")
VOICES_FILE: str = os.environ.get("VOICES_FILE", "voices-v1.0.bin")
DEFAULT_VOICE: str = os.environ.get("DEFAULT_VOICE", "af_heart")
