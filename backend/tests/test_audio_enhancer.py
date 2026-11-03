import numpy as np
import pytest
from services.audio_enhancer import estimate_snr_db, apply_spectral_subtraction
from services.feature_extractor import extract_acoustic_features


def test_estimate_snr_db_synthetic_signal():
    sr = 16000
    t = np.linspace(0, 1.0, sr, endpoint=False)
    # Pure tone with low noise
    signal = 0.5 * np.sin(2 * np.pi * 440 * t)
    noise = 0.01 * np.random.normal(0, 1, sr)
    audio = (signal + noise).astype(np.float32)

    snr = estimate_snr_db(audio, sr)
    assert snr > 15.0


def test_apply_spectral_subtraction_retains_shape():
    sr = 16000
    t = np.linspace(0, 1.0, sr, endpoint=False)
    signal = 0.5 * np.sin(2 * np.pi * 220 * t)
    noise = 0.05 * np.random.normal(0, 1, sr)
    audio = (signal + noise).astype(np.float32)

    cleaned, snr = apply_spectral_subtraction(audio, sr)
    assert len(cleaned) == len(audio)
    assert isinstance(snr, float)
    assert snr >= 0.0


def test_extract_acoustic_features_includes_snr():
    sr = 16000
    t = np.linspace(0, 1.0, sr, endpoint=False)
    audio = (0.5 * np.sin(2 * np.pi * 300 * t)).astype(np.float32)

    feats = extract_acoustic_features(audio, sr)
    assert hasattr(feats, "snr_db")
    assert feats.snr_db is not None
    assert feats.snr_db >= 0.0
