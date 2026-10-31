import io
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from main import app
from services.audio_transcoder import sniff_audio_format, decode_audio_stream
from services.audio_validator import validate_and_decode_audio
from tests.conftest import make_wav_bytes


@pytest.fixture
def client():
    return TestClient(app)


def test_sniff_audio_format_magic_signatures():
    # WAV magic signature
    wav_bytes = b"RIFF\x24\x00\x00\x00WAVEfmt "
    assert sniff_audio_format(wav_bytes, "test.wav") == "wav"

    # MP3 ID3 magic signature
    mp3_id3 = b"ID3\x03\x00\x00\x00\x00\x00\x00"
    assert sniff_audio_format(mp3_id3, "test.mp3") == "mp3"

    # MP3 frame sync signature
    mp3_sync = b"\xff\xfb\x90\x44" + b"\x00" * 32
    assert sniff_audio_format(mp3_sync, "stream.bin") == "mp3"

    # OGG container signature
    ogg_bytes = b"OggS\x00\x02\x00\x00\x00\x00"
    assert sniff_audio_format(ogg_bytes, "voice.ogg") == "ogg"

    # FLAC signature
    flac_bytes = b"fLaC\x00\x00\x00\x22"
    assert sniff_audio_format(flac_bytes, "track.flac") == "flac"

    # M4A signature
    m4a_bytes = b"\x00\x00\x00\x20ftypM4A "
    assert sniff_audio_format(m4a_bytes, "recording.m4a") == "m4a"


def test_sniff_audio_format_rejects_unknown():
    with pytest.raises(HTTPException) as exc:
        sniff_audio_format(b"PDF-1.4\x0a\x25\xe2", "document.pdf")
    assert exc.value.status_code == 400
    assert "Unsupported or unrecognizable" in exc.value.detail


def test_decode_audio_stream_wav():
    raw_wav = make_wav_bytes(channels=1, sample_rate=16000, seconds=0.2)
    mono_audio, sr, channels, fmt = decode_audio_stream(raw_wav, "sample.wav")
    assert fmt == "wav"
    assert sr == 16000
    assert channels == 1
    assert len(mono_audio) == int(16000 * 0.2)
    assert mono_audio.dtype == "float32"


def test_validate_and_decode_audio_duration_bounds():
    # Audio under 0.1s should raise 400
    too_short_wav = make_wav_bytes(channels=1, sample_rate=16000, seconds=0.05)
    with pytest.raises(HTTPException) as exc:
        validate_and_decode_audio(too_short_wav, "short.wav")
    assert exc.value.status_code == 400
    assert "too short" in exc.value.detail.lower()


def test_analyze_endpoint_accepts_wav(client, mono_wav):
    response = client.post(
        "/api/v1/analyze",
        files={"file": ("voice_sample.wav", mono_wav, "audio/wav")}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["filename"] == "voice_sample.wav"


def test_analyze_endpoint_rejects_unsupported_extension(client):
    response = client.post(
        "/api/v1/analyze",
        files={"file": ("malicious.exe", b"MZ\x90\x00", "application/x-msdownload")}
    )
    assert response.status_code == 400
    assert "Unsupported audio format" in response.json()["detail"]
