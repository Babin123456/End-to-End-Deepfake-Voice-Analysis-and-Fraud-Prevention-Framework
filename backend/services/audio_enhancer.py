import numpy as np
from scipy import signal
from typing import Tuple


def estimate_snr_db(audio: np.ndarray, sample_rate: int) -> float:
    """
    Estimates Signal-to-Noise Ratio (SNR) in dB using frequency domain spectral
    signal-to-noise floor estimation.
    """
    if len(audio) == 0:
        return 0.0

    nperseg = min(512, max(64, len(audio)))
    noverlap = nperseg // 2

    freqs, _, zxx = signal.stft(
        audio,
        fs=sample_rate,
        nperseg=nperseg,
        noverlap=noverlap,
        boundary=None,
    )

    power = np.abs(zxx) ** 2
    avg_power_per_bin = np.mean(power, axis=1)

    noise_floor = np.median(avg_power_per_bin)
    peak_signal = np.max(avg_power_per_bin)

    if noise_floor <= 1e-12:
        return 50.0

    snr = 10.0 * np.log10(max(1.0, peak_signal / noise_floor))
    return float(np.clip(snr, 0.0, 60.0))


def apply_spectral_subtraction(
    audio: np.ndarray,
    sample_rate: int,
    noise_factor: float = 0.8,
) -> Tuple[np.ndarray, float]:
    """
    Applies gentle spectral noise reduction to suppress static recording noise.
    Returns cleaned mono float32 array and estimated SNR in dB.
    """
    if len(audio) < 256:
        return audio.astype(np.float32), round(estimate_snr_db(audio, sample_rate), 1)

    nperseg = min(512, max(128, len(audio) // 4))
    noverlap = nperseg // 2

    _, _, zxx = signal.stft(
        audio,
        fs=sample_rate,
        nperseg=nperseg,
        noverlap=noverlap,
        boundary='zeros',
    )

    magnitude = np.abs(zxx)
    phase = np.angle(zxx)

    # Estimate noise spectrum as the lower quartile across time frames
    noise_spectrum = np.percentile(magnitude, 20, axis=1, keepdims=True)

    # Spectral subtraction with safety floor to prevent musical artifact distortion
    cleaned_mag = np.maximum(magnitude - noise_factor * noise_spectrum, 0.1 * magnitude)

    cleaned_zxx = cleaned_mag * np.exp(1j * phase)

    _, cleaned_audio = signal.istft(
        cleaned_zxx,
        fs=sample_rate,
        nperseg=nperseg,
        noverlap=noverlap,
        boundary='zeros',
    )

    if len(cleaned_audio) > len(audio):
        cleaned_audio = cleaned_audio[:len(audio)]
    elif len(cleaned_audio) < len(audio):
        cleaned_audio = np.pad(cleaned_audio, (0, len(audio) - len(cleaned_audio)))

    cleaned_audio = np.clip(cleaned_audio, -1.0, 1.0).astype(np.float32)
    snr_db = estimate_snr_db(cleaned_audio, sample_rate)

    return cleaned_audio, round(snr_db, 1)
