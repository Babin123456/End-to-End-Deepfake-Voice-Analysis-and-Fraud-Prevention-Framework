def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_analyze_unsupported_format(client):
    files = {"file": ("malicious.exe", b"executable_binary_data", "application/octet-stream")}
    response = client.post("/api/v1/analyze", files=files)
    assert response.status_code == 400
    assert "unsupported" in response.json()["detail"].lower()


def test_analyze_valid_wav(client, valid_wav_bytes):
    files = {"file": ("sample.wav", valid_wav_bytes, "audio/wav")}
    response = client.post("/api/v1/analyze", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "sample.wav"
    assert "fake_probability" in data
