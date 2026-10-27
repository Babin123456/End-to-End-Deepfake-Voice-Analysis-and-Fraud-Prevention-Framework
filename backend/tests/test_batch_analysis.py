import io
import pytest
from fastapi.testclient import TestClient
from main import app
from tests.conftest import make_wav_bytes


@pytest.fixture
def client():
    return TestClient(app)


def test_batch_analyze_multiple_valid_files(client):
    wav1 = make_wav_bytes(channels=1, sample_rate=16000, seconds=0.5)
    wav2 = make_wav_bytes(channels=1, sample_rate=16000, seconds=0.6)
    wav3 = make_wav_bytes(channels=2, sample_rate=16000, seconds=0.5)

    files = [
        ("files", ("call_sample_1.wav", wav1, "audio/wav")),
        ("files", ("call_sample_2.wav", wav2, "audio/wav")),
        ("files", ("call_sample_3.wav", wav3, "audio/wav")),
    ]

    response = client.post("/api/v1/analyze/batch", files=files)
    assert response.status_code == 200
    data = response.json()

    assert data["batch_id"].startswith("BATCH-")
    assert "timestamp" in data

    summary = data["summary"]
    assert summary["total_files"] == 3
    assert summary["successful_scans"] == 3
    assert summary["failed_scans"] == 0
    assert summary["campaign_threat_level"] in ["LOW", "ELEVATED", "CRITICAL"]

    items = data["items"]
    assert len(items) == 3
    for item in items:
        assert item["status"] == "completed"
        assert 0.0 <= item["fake_probability"] <= 1.0
        assert len(item["sha256_hash"]) == 64
        assert item["incident_id"].startswith("INC-")


def test_batch_analyze_partial_failure_resilience(client):
    valid_wav = make_wav_bytes(channels=1, sample_rate=16000, seconds=0.5)
    corrupted_data = b"NOT_A_VALID_WAV_CONTENT"

    files = [
        ("files", ("genuine_call.wav", valid_wav, "audio/wav")),
        ("files", ("malformed_recording.wav", corrupted_data, "audio/wav")),
    ]

    response = client.post("/api/v1/analyze/batch", files=files)
    assert response.status_code == 200
    data = response.json()

    summary = data["summary"]
    assert summary["total_files"] == 2
    assert summary["successful_scans"] == 1
    assert summary["failed_scans"] == 1

    items = data["items"]
    valid_item = next(i for i in items if i["filename"] == "genuine_call.wav")
    assert valid_item["status"] == "completed"
    assert valid_item["fake_probability"] is not None

    failed_item = next(i for i in items if i["filename"] == "malformed_recording.wav")
    assert failed_item["status"] == "error"
    assert failed_item["error_message"] is not None


def test_batch_analyze_missing_files(client):
    response = client.post("/api/v1/analyze/batch")
    assert response.status_code == 422
