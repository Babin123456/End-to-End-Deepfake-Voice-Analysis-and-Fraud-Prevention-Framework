from typing import Optional
from pydantic import BaseModel, Field


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
