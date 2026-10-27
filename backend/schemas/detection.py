from typing import Optional
from pydantic import BaseModel, Field

try:
    from schemas.audio import AcousticFeatures
    from schemas.fraud import FraudRiskReport
except ImportError:
    from backend.schemas.audio import AcousticFeatures
    from backend.schemas.fraud import FraudRiskReport


class ForensicBreakdown(BaseModel):
    spectral_consistency: float = Field(..., description="Score 0-100 indicating spectral naturalness")
    pitch_naturalness: float = Field(..., description="Score 0-100 indicating natural biological pitch micro-tremors")
    vocoder_artifact_score: float = Field(..., description="Score 0-100 indicating presence of neural synthesis artifacts")


class DetectionResult(BaseModel):
    fake_probability: float = Field(..., description="Estimated synthetic probability (0.0 to 1.0)")
    confidence_score: float = Field(..., description="Confidence percentage of the forensic verdict (0.0 to 100.0)")
    risk_level: str = Field(..., description="Risk tier: LOW_RISK, SUSPICIOUS, or HIGH_RISK_DEEPFAKE")
    indicators: list[str] = Field(default_factory=list, description="Forensic red flags or verification notes")
    breakdown: ForensicBreakdown


class AnalysisResponse(BaseModel):
    filename: str = Field(..., description="Name of the analyzed audio file")
    status: str = Field("completed", description="Analysis execution state")
    fake_probability: float = Field(..., description="Calculated probability that the voice sample is synthetic (0.0 to 1.0)")
    confidence_score: float = Field(..., description="Confidence percentage of the forensic verdict (0.0 to 100.0)")
    risk_level: str = Field(..., description="Risk categorization: LOW_RISK, SUSPICIOUS, or HIGH_RISK_DEEPFAKE")
    indicators: list[str] = Field(default_factory=list, description="Forensic red flags or verification notes")
    breakdown: ForensicBreakdown = Field(..., description="Forensic breakdown component scores")
    features: AcousticFeatures = Field(..., description="Extracted physical and spectral acoustic features")
    fraud_prevention: FraudRiskReport = Field(..., description="Fraud risk report with recommended mitigation actions")
    incident_id: str = Field(..., description="Unique audit incident identifier")
    sha256_hash: str = Field(..., description="Cryptographic SHA-256 hash of the audio binary")

