import io
import sys
from pathlib import Path
import numpy as np
from scipy.io import wavfile
import pytest
from fastapi.testclient import TestClient

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from main import app


def create_test_wav_bytes(
    duration: float = 1.0,
    sample_rate: int = 16000,
    frequency: float = 300.0,
    is_stereo: bool = False,
) -> bytes:
    """Helper generating an in-memory WAV file for testing."""
    total_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, total_samples, endpoint=False)
    # Fundamental tone + harmonic
    signal = 0.7 * np.sin(2 * np.pi * frequency * t) + 0.3 * np.sin(2 * np.pi * 2 * frequency * t)
    audio = (signal * 16384).astype(np.int16)

    if is_stereo:
        audio = np.column_stack((audio, audio))

    buf = io.BytesIO()
    wavfile.write(buf, sample_rate, audio)
    return buf.getvalue()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def valid_wav_bytes():
    return create_test_wav_bytes(duration=1.2, sample_rate=16000, frequency=250.0)


@pytest.fixture
def stereo_wav_bytes():
    return create_test_wav_bytes(duration=1.0, sample_rate=22050, frequency=350.0, is_stereo=True)


@pytest.fixture
def short_wav_bytes():
    return create_test_wav_bytes(duration=0.1, sample_rate=16000)


@pytest.fixture
def corrupted_wav_bytes():
    return b"RIFF\x00\x00\x00\x00WAVEfmt \x10\x00\x00\x00CORRUPTED_GARBAGE_PAYLOAD"
