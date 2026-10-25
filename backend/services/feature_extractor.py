import numpy as np
from scipy import signal

try:
    from schemas.audio import AcousticFeatures
except ImportError:
    from backend.schemas.audio import AcousticFeatures


def extract_acoustic_features(audio: np.ndarray, sample_rate: int, channels: int = 1) -> AcousticFeatures:
    """
    Extracts forensic acoustic features from normalized mono audio.
    """
    duration = float(len(audio)) / float(sample_rate)

    signs = np.signbit(audio)
    zcr = float(np.mean(signs[:-1] != signs[1:]))

    rms_energy = float(np.sqrt(np.mean(audio ** 2)))

    nperseg = min(1024, max(64, len(audio)))
    noverlap = nperseg // 2

    freqs, _, zxx = signal.stft(
        audio,
        fs=sample_rate,
        nperseg=nperseg,
        noverlap=noverlap,
        boundary=None,
    )

    mag_spec = np.abs(zxx) + 1e-10
    power_spec = mag_spec ** 2

    freq_grid = freqs[:, np.newaxis]
    total_energy = np.sum(mag_spec, axis=0)
    frame_centroids = np.sum(freq_grid * mag_spec, axis=0) / total_energy
    spectral_centroid = float(np.mean(frame_centroids))

    cumsum_power = np.cumsum(power_spec, axis=0)
    total_power = cumsum_power[-1:, :]
    rolloff_mask = cumsum_power >= (0.85 * total_power)
    rolloff_indices = np.argmax(rolloff_mask, axis=0)
    spectral_rolloff = float(np.mean(freqs[rolloff_indices]))

    eps = 1e-10
    log_power = np.log(power_spec + eps)
    geom_mean = np.exp(np.mean(log_power, axis=0))
    arith_mean = np.mean(power_spec, axis=0) + eps
    spectral_flatness = float(np.mean(geom_mean / arith_mean))

    f0_mean, jitter, shimmer = _estimate_pitch_and_perturbation(audio, sample_rate)

    return AcousticFeatures(
        sample_rate=sample_rate,
        duration_seconds=round(duration, 3),
        channels=channels,
        zero_crossing_rate=round(zcr, 4),
        rms_energy=round(rms_energy, 4),
        spectral_centroid_hz=round(spectral_centroid, 2),
        spectral_rolloff_hz=round(spectral_rolloff, 2),
        spectral_flatness=round(spectral_flatness, 4),
        fundamental_frequency_hz=round(f0_mean, 2) if f0_mean is not None else None,
        pitch_jitter=round(jitter, 4) if jitter is not None else None,
        shimmer=round(shimmer, 4) if shimmer is not None else None,
    )


def _estimate_pitch_and_perturbation(
    audio: np.ndarray, sample_rate: int
) -> tuple[float | None, float | None, float | None]:
    frame_len = int(0.04 * sample_rate)
    hop_len = int(0.02 * sample_rate)
    min_lag = max(1, int(sample_rate / 500))
    max_lag = min(frame_len - 1, int(sample_rate / 70))

    if len(audio) < frame_len or max_lag <= min_lag:
        return None, None, None

    f0_values = []
    amplitudes = []

    num_frames = (len(audio) - frame_len) // hop_len
    for i in range(num_frames):
        start = i * hop_len
        frame = audio[start : start + frame_len]
        frame = frame - np.mean(frame)
        frame_rms = np.sqrt(np.mean(frame ** 2))

        if frame_rms < 0.01:
            continue

        autocorr = np.correlate(frame, frame, mode="full")
        autocorr = autocorr[len(frame) - 1 :]
        r0 = autocorr[0] + 1e-10

        norm_autocorr = autocorr[min_lag:max_lag] / r0
        if len(norm_autocorr) == 0:
            continue

        peak_idx = int(np.argmax(norm_autocorr))
        peak_val = float(norm_autocorr[peak_idx])

        if peak_val > 0.35:
            lag = min_lag + peak_idx
            f0 = sample_rate / lag
            f0_values.append(f0)
            amplitudes.append(frame_rms)

    if len(f0_values) < 4:
        return None, None, None

    f0_arr = np.array(f0_values)
    amp_arr = np.array(amplitudes)

    f0_mean = float(np.mean(f0_arr))
    f0_diffs = np.abs(np.diff(f0_arr))
    jitter = float(np.mean(f0_diffs) / (f0_mean + 1e-10))

    amp_diffs = np.abs(np.diff(amp_arr))
    shimmer = float(np.mean(amp_diffs) / (np.mean(amp_arr) + 1e-10))

    return f0_mean, jitter, shimmer
