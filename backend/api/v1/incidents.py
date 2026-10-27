from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Response

try:
    from schemas.fraud import IncidentAuditLog
    from schemas.incidents import IncidentListResponse, IncidentStatsResponse
    from services.incident_service import (
        export_incidents_to_csv,
        get_incident_by_id,
        get_incident_stats,
        query_incidents,
    )
except ImportError:
    from backend.schemas.fraud import IncidentAuditLog
    from backend.schemas.incidents import IncidentListResponse, IncidentStatsResponse
    from backend.services.incident_service import (
        export_incidents_to_csv,
        get_incident_by_id,
        get_incident_stats,
        query_incidents,
    )

router = APIRouter(prefix="/incidents", tags=["Incidents & Audit Logs"])


@router.get("", response_model=IncidentListResponse)
def list_incidents(
    threat_category: Optional[str] = Query(None, description="Filter by threat category"),
    requires_human_escalation: Optional[bool] = Query(None, description="Filter by escalation requirement"),
    search: Optional[str] = Query(None, description="Search term for filename, hash, or incident ID"),
    limit: int = Query(50, ge=1, le=500, description="Page size limit"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
):
    """Retrieve filtered and paginated security incident audit records."""
    return query_incidents(
        threat_category=threat_category,
        requires_human_escalation=requires_human_escalation,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get("/stats", response_model=IncidentStatsResponse)
def get_stats():
    """Aggregate threat telemetry and incident escalation statistics."""
    return get_incident_stats()


@router.get("/export/csv")
def export_csv():
    """Export the full fraud audit trail as a downloadable CSV report."""
    csv_data = export_incidents_to_csv()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="fraud_audit_incidents.csv"'},
    )


@router.get("/{incident_id}", response_model=IncidentAuditLog)
def get_incident(incident_id: str):
    """Fetch details of a specific security incident by its unique ID."""
    incident = get_incident_by_id(incident_id)
    if not incident:
        raise HTTPException(
            status_code=404,
            detail=f"Security incident with ID '{incident_id}' not found.",
        )
    return incident
