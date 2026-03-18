from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.tts import TTSEngine

router = APIRouter()

# Populated once during application startup (see main.py lifespan).
engine: TTSEngine | None = None


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)
    voice: str = Field(default="af_heart")
    speed: float = Field(default=1.0, ge=0.5, le=2.0)


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/tts")
async def tts(req: TTSRequest):
    return StreamingResponse(
        engine.stream(req.text, voice=req.voice, speed=req.speed),
        media_type="audio/wav",
    )
