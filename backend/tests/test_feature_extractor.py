import numpy as np
import pytest


def test_zero_crossing_rate_calculation():
    # Pure square/sine wave
    t = np.linspace(0, 1.0, 16000)
    audio = np.sin(2 * np.pi * 100 * t)
    signs = np.signbit(audio)
    zcr = float(np.mean(signs[:-1] != signs[1:]))
    assert 0.0 < zcr < 1.0


def test_rms_energy_calculation():
    silence = np.zeros(16000, dtype=np.float32)
    tone = np.ones(16000, dtype=np.float32) * 0.5
    rms_silence = float(np.sqrt(np.mean(silence ** 2)))
    rms_tone = float(np.sqrt(np.mean(tone ** 2)))

    assert rms_silence == 0.0
    assert rms_tone == pytest.approx(0.5, abs=1e-5)
