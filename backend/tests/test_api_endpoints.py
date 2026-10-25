from main import MAX_UPLOAD_SIZE

ANALYZE = "/api/v1/analyze"


def test_root_returns_welcome_message(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to the Deepfake Audio Detection API"
    }


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
    assert body["status"] == "processing"


def test_stereo_wav_upload_is_accepted(client, stereo_wav):
    response = client.post(
        ANALYZE, files={"file": ("voice.WAVE", stereo_wav, "audio/wav")}
    )
    assert response.status_code == 200


def test_corrupted_header_is_not_checked_yet(client, corrupted_wav):
    # main.py only checks the file extension for now, so a .wav with a broken
    # header still gets through. Update this once header validation exists.
    response = client.post(
        ANALYZE, files={"file": ("broken.wav", corrupted_wav, "audio/wav")}
    )
    assert response.status_code == 200


def test_oversized_upload_gets_413(client):
    too_big = b"\0" * (MAX_UPLOAD_SIZE + 1)
    response = client.post(
        ANALYZE, files={"file": ("big.wav", too_big, "audio/wav")}
    )
    assert response.status_code == 413
    assert "too large" in response.json()["detail"]
