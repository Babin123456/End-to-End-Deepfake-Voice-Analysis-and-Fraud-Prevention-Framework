from typing import Optional
from pydantic import BaseModel, Field

try:
    from schemas.fraud import IncidentAuditLog
except ImportError:
    from backend.schemas.fraud import IncidentAuditLog


class IncidentListResponse(BaseModel):
    items: list[IncidentAuditLog] = Field(..., description="List of recorded security audit incidents")
    total_count: int = Field(..., description="Total count of incidents matching criteria")
    limit: int = Field(..., description="Maximum results per page")
    offset: int = Field(..., description="Number of skipped items")


class ThreatDistribution(BaseModel):
    category: str
    count: int
    percentage: float


class IncidentStatsResponse(BaseModel):
    total_incidents: int = Field(..., description="Total number of logged fraud incidents")
    escalated_incidents: int = Field(..., description="Incidents requiring immediate human escalation")
    escalation_rate_percentage: float = Field(..., description="Percentage of incidents requiring escalation")
    average_fake_probability: float = Field(..., description="Mean synthetic probability across all incidents")
    threat_breakdown: list[ThreatDistribution] = Field(default_factory=list, description="Distribution of threat categories")
