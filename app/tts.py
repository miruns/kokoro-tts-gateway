import struct

import numpy as np
from kokoro_onnx import Kokoro


class TTSEngine:
    """Thin wrapper around kokoro-onnx that yields streamable WAV chunks."""

    def __init__(self, model_path: str, voices_path: str) -> None:
        self.kokoro = Kokoro(model_path, voices_path)

    def stream(
        self,
        text: str,
        voice: str = "af_heart",
        speed: float = 1.0,
    ):
        """Yield a WAV header followed by PCM-16 audio chunks."""
        sample_rate = 24000
        yield _wav_header(sample_rate)

        for samples, _sr in self.kokoro.create_stream(
            text, voice=voice, speed=speed
        ):
            pcm = (samples * 32767).clip(-32768, 32767).astype(np.int16)
            yield pcm.tobytes()


def _wav_header(
    sample_rate: int = 24000,
    bits_per_sample: int = 16,
    channels: int = 1,
) -> bytes:
    """Build a WAV header with an unknown data length (streaming-safe).

    Setting the data chunk size to 0x7FFFFFFF signals to decoders that the
    total length is not known upfront and they should read until EOF.
    """
    data_size = 0x7FFFFFFF
    byte_rate = sample_rate * channels * bits_per_sample // 8
    block_align = channels * bits_per_sample // 8
    return struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        data_size + 36,
        b"WAVE",
        b"fmt ",
        16,
        1,              # PCM format
        channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b"data",
        data_size,
    )
