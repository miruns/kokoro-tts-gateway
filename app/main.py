from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.auth import APIKeyMiddleware
from app.config import MODEL_DIR, MODEL_FILE, VOICES_FILE
from app.tts import TTSEngine
import app.routes as routes_module


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the Kokoro model once at startup; release on shutdown."""
    routes_module.engine = TTSEngine(
        model_path=f"{MODEL_DIR}/{MODEL_FILE}",
        voices_path=f"{MODEL_DIR}/{VOICES_FILE}",
    )
    yield
    routes_module.engine = None


app = FastAPI(title="Kokoro TTS Gateway", lifespan=lifespan)
app.add_middleware(APIKeyMiddleware)
app.include_router(routes_module.router)
