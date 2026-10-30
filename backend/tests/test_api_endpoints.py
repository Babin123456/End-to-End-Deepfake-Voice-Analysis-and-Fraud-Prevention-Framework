from main import MAX_UPLOAD_SIZE

ANALYZE = "/api/v1/analyze"


def test_root_returns_welcome_message(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to the Deepfake Audio Detection & Fraud Prevention API"
    assert data["version"] == "1.0.0"
    assert data["service"] == "deepfake-voice-analysis-engine"


def test_non_wav_upload_is_rejected(client):
    response = client.post(
        ANALYZE, files={"file": ("voice.mp3", b"not audio", "audio/mpeg")}
    )
    assert response.status_code == 400
    assert "Unsupported audio format" in response.json()["detail"]


def test_missing_file_is_a_validation_error(client):
    assert client.post(ANALYZE).status_code == 422


def test_mono_wav_upload_is_accepted(client, mono_wav):
    response = client.post(
        ANALYZE, files={"file": ("voice.wav", mono_wav, "audio/wav")}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "voice.wav"
    assert body["status"] == "completed"
    assert 0.0 <= body["fake_probability"] <= 1.0
    assert "features" in body
    assert "breakdown" in body
    assert "fraud_prevention" in body
    assert "incident_id" in body
    assert len(body["sha256_hash"]) == 64


def test_stereo_wav_upload_is_accepted(client, stereo_wav):
    response = client.post(
        ANALYZE, files={"file": ("voice.WAVE", stereo_wav, "audio/wav")}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["features"]["channels"] == 2


def test_corrupted_header_is_rejected(client, corrupted_wav):
    response = client.post(
        ANALYZE, files={"file": ("broken.wav", corrupted_wav, "audio/wav")}
    )
    assert response.status_code == 400
    assert "Corrupted audio header" in response.json()["detail"]


def test_empty_wav_upload_is_rejected(client):
    response = client.post(
        ANALYZE, files={"file": ("empty.wav", b"", "audio/wav")}
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()



def test_oversized_upload_gets_413(client):
    too_big = b"\0" * (MAX_UPLOAD_SIZE + 1)
    response = client.post(
        ANALYZE, files={"file": ("big.wav", too_big, "audio/wav")}
    )
    assert response.status_code == 413
    assert "too large" in response.json()["detail"]
