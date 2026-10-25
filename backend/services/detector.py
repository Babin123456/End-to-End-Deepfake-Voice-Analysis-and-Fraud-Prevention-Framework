import numpy as np

try:
    from core.constants import (
        HUMAN_MIN_JITTER,
        HUMAN_MAX_JITTER,
        HUMAN_MIN_SHIMMER,
        RISK_THRESHOLD_LOW,
        RISK_THRESHOLD_HIGH,
        RISK_LEVEL_LOW,
        RISK_LEVEL_SUSPICIOUS,
        RISK_LEVEL_HIGH,
    )
    from schemas.detection import DetectionResult, ForensicBreakdown
    from services.vocoder_analyzer import analyze_vocoder_artifacts
except ImportError:
    from backend.core.constants import (
        HUMAN_MIN_JITTER,
        HUMAN_MAX_JITTER,
        HUMAN_MIN_SHIMMER,
        RISK_THRESHOLD_LOW,
        RISK_THRESHOLD_HIGH,
        RISK_LEVEL_LOW,
        RISK_LEVEL_SUSPICIOUS,
        RISK_LEVEL_HIGH,
    )
    from backend.schemas.detection import DetectionResult, ForensicBreakdown
    from backend.services.vocoder_analyzer import analyze_vocoder_artifacts


def detect_synthetic_voice(
    audio: np.ndarray,
    sample_rate: int,
    pitch_jitter: float | None = None,
    shimmer: float | None = None,
    spectral_flatness: float = 0.0,
) -> DetectionResult:
    """
    Evaluates multi-heuristic forensic features to calculate the probability
    of synthetic or deepfake voice manipulation.
    """
    indicators: list[str] = []
    synthetic_factors: list[float] = []

    # 1. Pitch Jitter Evaluation (Biological vocal cord micro-perturbations)
    pitch_naturalness = 85.0
    if pitch_jitter is not None:
        if pitch_jitter < HUMAN_MIN_JITTER:
            # Unnatural robotic pitch consistency (TTS/voice cloning)
            prob_pitch = min(1.0, (HUMAN_MIN_JITTER - pitch_jitter) / HUMAN_MIN_JITTER + 0.5)
            synthetic_factors.append(prob_pitch * 0.35)
            pitch_naturalness = max(10.0, 100.0 - (prob_pitch * 90.0))
            indicators.append("Unnaturally low pitch jitter: vocal cord pitch micro-variation is absent")
        elif pitch_jitter > HUMAN_MAX_JITTER:
            # Chaotic pitch tracking often seen in low-quality voice conversion models
            synthetic_factors.append(0.65 * 0.35)
            pitch_naturalness = 45.0
            indicators.append("Irregular pitch jitter: unnatural vocal frequency perturbations detected")
        else:
            # Natural human pitch jitter
            synthetic_factors.append(0.05 * 0.35)
            pitch_naturalness = 95.0
    else:
        synthetic_factors.append(0.15 * 0.35)

    # 2. Shimmer Evaluation (Biological respiratory amplitude micro-variation)
    if shimmer is not None:
        if shimmer < HUMAN_MIN_SHIMMER:
            prob_shimmer = min(1.0, (HUMAN_MIN_SHIMMER - shimmer) / HUMAN_MIN_SHIMMER + 0.4)
            synthetic_factors.append(prob_shimmer * 0.25)
            indicators.append("Unnatural amplitude shimmer: respiratory micro-tremor amplitude is suppressed")
        else:
            synthetic_factors.append(0.08 * 0.25)
    else:
        synthetic_factors.append(0.12 * 0.25)

    # 3. Neural Vocoder Artifacts
    vocoder_score, vocoder_indicators = analyze_vocoder_artifacts(audio, sample_rate)
    indicators.extend(vocoder_indicators)
    synthetic_factors.append((vocoder_score / 100.0) * 0.40)

    # 4. Spectral Consistency
    spectral_consistency = max(15.0, min(100.0, 100.0 - (spectral_flatness * 80.0) - (vocoder_score * 0.3)))

    # Compute aggregate probability
    fake_probability = float(np.clip(sum(synthetic_factors), 0.0, 0.99))

    # Determine risk level
    if fake_probability < RISK_THRESHOLD_LOW:
        risk_level = RISK_LEVEL_LOW
        if not indicators:
            indicators.append("Acoustic parameters align with natural human speech characteristics")
    elif fake_probability < RISK_THRESHOLD_HIGH:
        risk_level = RISK_LEVEL_SUSPICIOUS
        indicators.append("Acoustic profile exhibits mixed natural and synthetic signatures")
    else:
        risk_level = RISK_LEVEL_HIGH
        indicators.append("Critical forensic anomalies detected: voice shows high likelihood of AI synthesis")

    # Confidence score based on sample duration and feature completeness
    confidence = 90.0 if (pitch_jitter is not None and shimmer is not None) else 75.0

    breakdown = ForensicBreakdown(
        spectral_consistency=round(spectral_consistency, 1),
        pitch_naturalness=round(pitch_naturalness, 1),
        vocoder_artifact_score=round(vocoder_score, 1),
    )

    return DetectionResult(
        fake_probability=round(fake_probability, 3),
        confidence_score=round(confidence, 1),
        risk_level=risk_level,
        indicators=indicators,
        breakdown=breakdown,
    )
