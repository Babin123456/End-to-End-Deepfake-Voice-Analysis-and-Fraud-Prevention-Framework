import io
import struct
import wave
import pytest
from fastapi.testclient import TestClient
from main import app
from schemas.detection import AnalysisResponse


@pytest.fixture
def client():
    return TestClient(app)


def generate_test_wav(duration=0.5, sample_rate=16000, frequency=440.0):
    """Generates an in-memory test tone WAV file."""
    import numpy as np
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    # Generate audio signal with harmonics
    waveform = (0.5 * np.sin(2 * np.pi * frequency * t) +
                0.25 * np.sin(2 * np.pi * (frequency * 2) * t))
    audio_int16 = (waveform * 32767).astype(np.int16)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(audio_int16.tobytes())
    return buf.getvalue()


def test_full_pipeline_response_structure(client):
    audio_bytes = generate_test_wav(duration=0.5, sample_rate=16000, frequency=220.0)
    response = client.post(
        "/api/v1/analyze",
        files={"file": ("sample_vocal.wav", audio_bytes, "audio/wav")}
    )
    assert response.status_code == 200
    data = response.json()

    # Validate schema conformity
    validated = AnalysisResponse(**data)
    assert validated.filename == "sample_vocal.wav"
    assert validated.status == "completed"
    assert 0.0 <= validated.fake_probability <= 1.0
    assert 0.0 <= validated.confidence_score <= 100.0
    assert validated.risk_level in ["LOW_RISK", "SUSPICIOUS", "HIGH_RISK_DEEPFAKE"]
    assert len(validated.indicators) > 0

    # Validate acoustic features
    assert validated.features.sample_rate == 16000
    assert validated.features.channels == 1
    assert validated.features.duration_seconds >= 0.49

    # Validate fraud prevention fields
    assert validated.fraud_prevention.sha256_hash == validated.sha256_hash
    assert 0.0 <= validated.fraud_prevention.impersonation_threat_score <= 100.0
    assert len(validated.fraud_prevention.advisory_actions) > 0
    assert validated.incident_id.startswith("INC-")


def test_audio_too_short_is_rejected(client):
    """Audio below 0.1s minimum duration is rejected with HTTP 400."""
    short_audio = generate_test_wav(duration=0.04, sample_rate=16000)
    response = client.post(
        "/api/v1/analyze",
        files={"file": ("too_short.wav", short_audio, "audio/wav")}
    )
    assert response.status_code == 400
    assert "too short" in response.json()["detail"].lower()


def test_incident_id_is_unique(client):
    audio_bytes = generate_test_wav(duration=0.3, sample_rate=16000)
    resp1 = client.post(
        "/api/v1/analyze",
        files={"file": ("test1.wav", audio_bytes, "audio/wav")}
    )
    resp2 = client.post(
        "/api/v1/analyze",
        files={"file": ("test2.wav", audio_bytes, "audio/wav")}
    )
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    id1 = resp1.json()["incident_id"]
    id2 = resp2.json()["incident_id"]
    assert id1 != id2
