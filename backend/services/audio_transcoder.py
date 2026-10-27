import io
import struct
import numpy as np
from fastapi import HTTPException
from scipy.io import wavfile

# Magic headers for container sniffing
MAGIC_RIFF = b"RIFF"
MAGIC_WAVE = b"WAVE"
MAGIC_ID3 = b"ID3"
MAGIC_OGG = b"OggS"
MAGIC_FLAC = b"fLaC"


def sniff_audio_format(raw_bytes: bytes, filename: str = "") -> str:
    """
    Detects audio container format using binary magic signatures and file extension.
    Returns: 'wav', 'mp3', 'ogg', 'flac', 'm4a', or raises HTTPException if unknown.
    """
    if not raw_bytes or len(raw_bytes) < 4:
        raise HTTPException(
            status_code=400,
            detail="The uploaded audio file is empty or corrupted.",
        )

    # Magic byte checks
    if len(raw_bytes) >= 12 and raw_bytes.startswith(MAGIC_RIFF) and MAGIC_WAVE in raw_bytes[:16]:
        return "wav"
    if raw_bytes.startswith(MAGIC_ID3) or (len(raw_bytes) >= 2 and raw_bytes[0] == 0xFF and (raw_bytes[1] & 0xE0) == 0xE0):
        return "mp3"
    if raw_bytes.startswith(MAGIC_OGG):
        return "ogg"
    if raw_bytes.startswith(MAGIC_FLAC):
        return "flac"
    if len(raw_bytes) >= 8 and raw_bytes[4:8] in (b"ftyp", b"moov"):
        return "m4a"

    # Extension fallback
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if ext in ("wav", "wave"):
        return "wav"
    if ext == "mp3":
        return "mp3"
    if ext == "ogg":
        return "ogg"
    if ext == "flac":
        return "flac"
    if ext in ("m4a", "aac"):
        return "m4a"

    raise HTTPException(
        status_code=400,
        detail="Unsupported or unrecognizable audio format. Supported formats: WAV, MP3, OGG, FLAC, M4A.",
    )


def decode_audio_stream(raw_bytes: bytes, filename: str = "") -> tuple[np.ndarray, int, int, str]:
    """
    Transcodes and normalizes an input audio stream into mono float32 array,
    sample rate, original channel count, and detected format name.
    """
    fmt = sniff_audio_format(raw_bytes, filename)

    if fmt == "wav":
        buffer = io.BytesIO(raw_bytes)
        try:
            sample_rate, audio_data = wavfile.read(buffer)
        except Exception as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to parse WAV audio stream: {str(exc)}",
            )
        mono_audio, channels = _normalize_audio_channels(audio_data)
        return mono_audio, int(sample_rate), int(channels), "wav"

    # Attempt to decode non-WAV formats using available audio engines
    try:
        import soundfile as sf
        buffer = io.BytesIO(raw_bytes)
        audio_data, sample_rate = sf.read(buffer, dtype="float32")
        mono_audio, channels = _normalize_audio_channels(audio_data)
        return mono_audio, int(sample_rate), int(channels), fmt
    except ImportError:
        pass
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to transcode {fmt.upper()} audio stream: {str(exc)}",
        )

    # Fallback to pydub if soundfile is unavailable
    try:
        from pydub import AudioSegment
        buffer = io.BytesIO(raw_bytes)
        segment = AudioSegment.from_file(buffer, format=fmt)
        samples = np.array(segment.get_array_of_samples(), dtype=np.float32)
        channels = segment.channels
        if channels == 2:
            audio_data = samples.reshape((-1, 2))
            mono_audio = np.mean(audio_data, axis=1, dtype=np.float32)
        else:
            mono_audio = samples
        mono_audio /= 32768.0
        return mono_audio, int(segment.frame_rate), int(channels), fmt
    except ImportError:
        pass
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Transcoding error for {fmt.upper()}: {str(exc)}",
        )

    # If neither non-standard library is installed, provide clear instructions
    raise HTTPException(
        status_code=400,
        detail=f"Decoded {fmt.upper()} container, but audio transcoding requires soundfile or pydub. Please upload standard PCM .wav.",
    )


def _normalize_audio_channels(audio_data: np.ndarray) -> tuple[np.ndarray, int]:
    """Converts multi-channel integer/float audio to float32 mono scaled [-1.0, 1.0]."""
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

    return mono_audio, channels
