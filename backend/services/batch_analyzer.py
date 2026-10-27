import datetime
import uuid
from typing import Optional

try:
    from core.security import compute_sha256
    from schemas.batch import BatchAnalysisResponse, BatchItemResult, BatchSummaryStats
    from services.audio_validator import validate_and_decode_wav
    from services.audit_logger import log_fraud_incident
    from services.detector import detect_synthetic_voice
    from services.feature_extractor import extract_acoustic_features
    from services.fraud_engine import evaluate_fraud_risk
except ImportError:
    from backend.core.security import compute_sha256
    from backend.schemas.batch import BatchAnalysisResponse, BatchItemResult, BatchSummaryStats
    from backend.services.audio_validator import validate_and_decode_wav
    from backend.services.audit_logger import log_fraud_incident
    from backend.services.detector import detect_synthetic_voice
    from backend.services.feature_extractor import extract_acoustic_features
    from backend.services.fraud_engine import evaluate_fraud_risk


def process_single_audio_item(filename: str, contents: bytes) -> BatchItemResult:
    """Processes an isolated audio sample within a batch, returning structured result or error."""
    if not contents:
        return BatchItemResult(
            filename=filename,
            status="error",
            error_message="Uploaded audio file content is empty.",
        )

    try:
        # Decode and validate WAV audio
        audio, sample_rate, channels = validate_and_decode_wav(contents)

        # Extract acoustic and spectral features
        features = extract_acoustic_features(audio, sample_rate=sample_rate, channels=channels)

        # Run synthetic voice detector
        detection = detect_synthetic_voice(
            audio=audio,
            sample_rate=sample_rate,
            pitch_jitter=features.pitch_jitter,
            shimmer=features.shimmer,
            spectral_flatness=features.spectral_flatness,
        )

        # Cryptographic hash
        sha256_hash = compute_sha256(contents)

        # Fraud risk evaluation
        fraud_report = evaluate_fraud_risk(
            fake_probability=detection.fake_probability,
            sha256_hash=sha256_hash,
            duration_seconds=features.duration_seconds,
        )

        # Audit incident logging
        incident = log_fraud_incident(
            filename=filename,
            sha256_hash=sha256_hash,
            fake_probability=detection.fake_probability,
            threat_category=fraud_report.threat_category,
            requires_human_escalation=fraud_report.requires_human_escalation,
        )

        return BatchItemResult(
            filename=filename,
            status="completed",
            fake_probability=detection.fake_probability,
            confidence_score=detection.confidence_score,
            risk_level=detection.risk_level,
            threat_category=fraud_report.threat_category,
            requires_human_escalation=fraud_report.requires_human_escalation,
            incident_id=incident.incident_id,
            sha256_hash=sha256_hash,
        )
    except Exception as exc:
        detail = getattr(exc, "detail", str(exc))
        return BatchItemResult(
            filename=filename,
            status="error",
            error_message=str(detail),
        )


def analyze_audio_batch(file_items: list[tuple[str, bytes]]) -> BatchAnalysisResponse:
    """
    Executes forensic analysis over a batch of audio files and compiles aggregate campaign metrics.
    """
    batch_id = f"BATCH-{uuid.uuid4().hex[:10].upper()}"
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    results: list[BatchItemResult] = []
    for filename, raw_bytes in file_items:
        item_res = process_single_audio_item(filename, raw_bytes)
        results.append(item_res)

    total_files = len(results)
    successful = [r for r in results if r.status == "completed" and r.fake_probability is not None]
    failed = [r for r in results if r.status == "error"]

    successful_count = len(successful)
    failed_count = len(failed)

    flagged_deepfakes = sum(1 for r in successful if (r.fake_probability or 0.0) >= 0.65)
    suspicious = sum(1 for r in successful if 0.35 <= (r.fake_probability or 0.0) < 0.65)
    authentic = sum(1 for r in successful if (r.fake_probability or 0.0) < 0.35)

    avg_fake = (
        round(sum(r.fake_probability or 0.0 for r in successful) / successful_count, 3)
        if successful_count > 0
        else 0.0
    )

    highest_risk_name: Optional[str] = None
    if successful:
        top_item = max(successful, key=lambda r: r.fake_probability or 0.0)
        highest_risk_name = top_item.filename

    if flagged_deepfakes > 0 or avg_fake >= 0.60:
        campaign_level = "CRITICAL"
    elif suspicious > 0 or avg_fake >= 0.35:
        campaign_level = "ELEVATED"
    else:
        campaign_level = "LOW"

    summary = BatchSummaryStats(
        total_files=total_files,
        successful_scans=successful_count,
        failed_scans=failed_count,
        flagged_deepfakes_count=flagged_deepfakes,
        suspicious_count=suspicious,
        authentic_count=authentic,
        average_fake_probability=avg_fake,
        highest_risk_filename=highest_risk_name,
        campaign_threat_level=campaign_level,
    )

    return BatchAnalysisResponse(
        batch_id=batch_id,
        timestamp=timestamp,
        summary=summary,
        items=results,
    )
