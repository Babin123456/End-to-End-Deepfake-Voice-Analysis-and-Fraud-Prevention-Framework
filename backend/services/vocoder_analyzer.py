import numpy as np


def analyze_vocoder_artifacts(audio: np.ndarray, sample_rate: int) -> tuple[float, list[str]]:
    """
    Analyzes audio for distinctive neural vocoder artifacts commonly produced
    by HiFi-GAN, WaveGrad, or diffusion-based voice synthesis models.
    Returns (artifact_score_0_to_100, detected_indicators).
    """
    indicators: list[str] = []
    score = 0.0

    if len(audio) < 256:
        return 0.0, ["Insufficient audio sample duration for vocoder analysis"]

    # Compute FFT magnitude spectrum
    n = len(audio)
    fft_vals = np.abs(np.fft.rfft(audio))
    freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate)

    # 1. High-Frequency Cliff Detection (Common in 16kHz/22kHz neural upsamplers)
    nyquist = sample_rate / 2.0
    cutoff_band = nyquist * 0.85
    high_freq_mask = freqs >= cutoff_band
    low_freq_mask = (freqs >= 300) & (freqs < cutoff_band)

    high_energy = np.mean(fft_vals[high_freq_mask]) if np.any(high_freq_mask) else 0.0
    low_energy = np.mean(fft_vals[low_freq_mask]) if np.any(low_freq_mask) else 1.0

    ratio = high_energy / (low_energy + 1e-10)

    # Abrupt high-frequency suppression typical in neural vocoders
    if ratio < 0.0005:
        score += 35.0
        indicators.append("Unnatural high-frequency spectral cutoff detected (vocoder band-limiting)")
    elif ratio < 0.002:
        score += 15.0

    # 2. Phase Discontinuity / Repetitive Harmonic Pattern Check
    diffs = np.diff(audio)
    discontinuity_ratio = float(np.sum(np.abs(diffs) > 0.85)) / float(len(diffs) + 1e-10)
    if discontinuity_ratio > 0.02:
        score += 30.0
        indicators.append("Acoustic phase discontinuities consistent with concatenative/diffusion artifacts")

    # 3. Dynamic Range Normalization Flatness
    quantiles = np.percentile(np.abs(audio), [10, 50, 90])
    p10, p50, p90 = quantiles[0], quantiles[1], quantiles[2]
    dynamic_range_ratio = (p90 - p10) / (p50 + 1e-10)
    if dynamic_range_ratio < 0.5:
        score += 25.0
        indicators.append("Excessive dynamic range compression typical in synthetic speech engines")

    return min(100.0, score), indicators
