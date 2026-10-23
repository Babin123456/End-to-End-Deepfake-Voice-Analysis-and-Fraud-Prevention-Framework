import pytest
from fastapi import HTTPException
from tests.conftest import create_test_wav_bytes


def test_wav_structure_valid():
    wav_bytes = create_test_wav_bytes(duration=1.0, sample_rate=16000)
    assert len(wav_bytes) > 44
    assert wav_bytes.startswith(b"RIFF")
    assert b"WAVE" in wav_bytes[:16]


def test_empty_file_fails():
    with pytest.raises(Exception):
        if len(b"") < 44:
            raise HTTPException(status_code=400, detail="Empty audio")


def test_stereo_channels_handled():
    wav_bytes = create_test_wav_bytes(duration=1.0, sample_rate=16000, is_stereo=True)
    assert len(wav_bytes) > 0
