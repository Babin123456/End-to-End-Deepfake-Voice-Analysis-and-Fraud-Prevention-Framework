from typing import Optional
from pydantic import BaseModel, Field

try:
    from schemas.audio import AcousticFeatures
    from schemas.detection import ForensicBreakdown
    from schemas.fraud import FraudRiskReport
except ImportError:
    from backend.schemas.audio import AcousticFeatures
    from backend.schemas.detection import ForensicBreakdown
    from backend.schemas.fraud import FraudRiskReport


class BatchItemResult(BaseModel):
    filename: str
    status: str = Field(..., description="Item status: completed or error")
    fake_probability: Optional[float] = Field(None, description="Calculated synthetic probability")
    confidence_score: Optional[float] = Field(None, description="Verdict confidence percentage")
    risk_level: Optional[str] = Field(None, description="LOW_RISK, SUSPICIOUS, or HIGH_RISK_DEEPFAKE")
    threat_category: Optional[str] = Field(None, description="Fraud classification vector")
    requires_human_escalation: Optional[bool] = Field(None, description="Escalation flag")
    incident_id: Optional[str] = Field(None, description="Audit incident ID")
    sha256_hash: Optional[str] = Field(None, description="Cryptographic SHA-256 fingerprint")
    error_message: Optional[str] = Field(None, description="Diagnostic error details if processing failed")


class BatchSummaryStats(BaseModel):
    total_files: int
    successful_scans: int
    failed_scans: int
    flagged_deepfakes_count: int
    suspicious_count: int
    authentic_count: int
    average_fake_probability: float
    highest_risk_filename: Optional[str] = None
    campaign_threat_level: str = Field(..., description="Overall risk posture: LOW, ELEVATED, CRITICAL")


class BatchAnalysisResponse(BaseModel):
    batch_id: str
    timestamp: str
    summary: BatchSummaryStats
    items: list[BatchItemResult]
