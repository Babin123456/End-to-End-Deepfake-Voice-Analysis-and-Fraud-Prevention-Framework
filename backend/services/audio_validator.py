import io
import numpy as np
from scipy.io import wavfile
from fastapi import HTTPException

try:
    from services.audio_transcoder import decode_audio_stream
except ImportError:
    from backend.services.audio_transcoder import decode_audio_stream


MIN_DURATION_SECONDS = 0.1
MAX_DURATION_SECONDS = 300.0


def validate_and_decode_audio(raw_bytes: bytes, filename: str = "") -> tuple[np.ndarray, int, int, str]:
    """
    Validates and decodes multi-format audio streams (WAV, MP3, OGG, FLAC, M4A)
    into mono float32, sample_rate, original channel count, and format name.
    """
    if not raw_bytes or len(raw_bytes) < 4:
        raise HTTPException(
            status_code=400,
            detail="The uploaded audio file is empty or corrupted.",
        )

    mono_audio, sample_rate, channels, fmt = decode_audio_stream(raw_bytes, filename=filename)

    if sample_rate <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid sampling rate detected in audio stream.",
        )

    duration = float(len(mono_audio)) / float(sample_rate)

    if duration < MIN_DURATION_SECONDS:
        raise HTTPException(
            status_code=400,
            detail=f"Audio sample is too short ({duration:.2f}s). Minimum required duration is {MIN_DURATION_SECONDS}s.",
        )

    if duration > MAX_DURATION_SECONDS:
        raise HTTPException(
            status_code=400,
            detail=f"Audio sample duration ({duration:.1f}s) exceeds maximum allowed length of {MAX_DURATION_SECONDS}s.",
        )

    return mono_audio, int(sample_rate), int(channels), fmt


def validate_and_decode_wav(raw_bytes: bytes) -> tuple[np.ndarray, int, int]:
    """
    Legacy WAV-specific validation helper for backward compatibility.
    """
    mono_audio, sample_rate, channels, _ = validate_and_decode_audio(raw_bytes, filename="sample.wav")
    return mono_audio, sample_rate, channels
