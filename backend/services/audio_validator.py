import io
import numpy as np
from scipy.io import wavfile
from fastapi import HTTPException


MIN_DURATION_SECONDS = 0.1
MAX_DURATION_SECONDS = 300.0


def validate_and_decode_wav(raw_bytes: bytes) -> tuple[np.ndarray, int, int]:
    """
    Validates a raw byte buffer as a canonical WAV file, converts it to mono float32,
    and returns (normalized_audio_array, sample_rate, original_channel_count).
    """
    if not raw_bytes or len(raw_bytes) < 44:
        raise HTTPException(
            status_code=400,
            detail="The uploaded audio file is empty or missing a valid WAV header.",
        )

    if not (raw_bytes.startswith(b"RIFF") and b"WAVE" in raw_bytes[:16]):
        raise HTTPException(
            status_code=400,
            detail="Corrupted audio header: file is not a valid RIFF/WAVE stream.",
        )

    buffer = io.BytesIO(raw_bytes)
    try:
        sample_rate, audio_data = wavfile.read(buffer)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to parse WAV audio stream: {str(exc)}",
        )

    if sample_rate <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid sampling rate detected in audio header.",
        )

    if audio_data.ndim == 1:
        channels = 1
        mono_audio = audio_data.astype(np.float32)
    elif audio_data.ndim == 2:
        channels = audio_data.shape[1]
        mono_audio = np.mean(audio_data, axis=1, dtype=np.float32)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio channel dimensions: {audio_data.ndim}",
        )

    if audio_data.dtype == np.int16:
        mono_audio /= 32768.0
    elif audio_data.dtype == np.int32:
        mono_audio /= 2147483648.0
    elif audio_data.dtype == np.uint8:
        mono_audio = (mono_audio - 128.0) / 128.0
    elif np.issubdtype(audio_data.dtype, np.floating):
        mono_audio = np.clip(mono_audio, -1.0, 1.0)

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

    return mono_audio, int(sample_rate), int(channels)
