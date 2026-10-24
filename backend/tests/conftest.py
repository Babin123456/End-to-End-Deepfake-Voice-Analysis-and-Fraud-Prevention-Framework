import io
import struct
import sys
import wave
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Tests run from backend/, so make `import main` work wherever pytest is started.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import app  # noqa: E402


def make_wav_bytes(channels=1, sample_rate=16000, seconds=0.1):
    """Build a small silent PCM WAV in memory with the stdlib wave module."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        frames = int(sample_rate * seconds)
        wav.writeframes(struct.pack("<h", 0) * frames * channels)
    return buf.getvalue()


@pytest.fixture
def mono_wav():
    return make_wav_bytes(channels=1)


@pytest.fixture
def stereo_wav():
    return make_wav_bytes(channels=2)


@pytest.fixture
def corrupted_wav(mono_wav):
    # Valid length, but the RIFF/WAVE magic bytes are overwritten.
    return b"XXXXXXXXXXXX" + mono_wav[12:]


@pytest.fixture
def client():
    return TestClient(app)
