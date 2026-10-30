import csv
import io
import json
import logging
from pathlib import Path
from typing import Optional

try:
    from schemas.fraud import IncidentAuditLog
    from schemas.incidents import IncidentListResponse, IncidentStatsResponse, ThreatDistribution
except ImportError:
    from backend.schemas.fraud import IncidentAuditLog
    from backend.schemas.incidents import IncidentListResponse, IncidentStatsResponse, ThreatDistribution

logger = logging.getLogger("fraud_prevention_audit")
_AUDIT_LOG_FILE = Path(__file__).resolve().parent.parent / "fraud_audit_events.log"


def read_all_incidents() -> list[IncidentAuditLog]:
    """Reads all raw incident audit events from disk in reverse chronological order."""
    if not _AUDIT_LOG_FILE.exists():
        return []

    incidents: list[IncidentAuditLog] = []
    try:
        with open(_AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                    incidents.append(IncidentAuditLog(**payload))
                except Exception as exc:
                    logger.debug("Skipping unparseable audit line: %s", exc)
    except Exception as exc:
        logger.error("Failed to read audit log file: %s", exc)
        return []

    # Sort descending by timestamp
    incidents.sort(key=lambda item: item.timestamp, reverse=True)
    return incidents


def query_incidents(
    threat_category: Optional[str] = None,
    requires_human_escalation: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> IncidentListResponse:
    """Filters, searches, and paginates stored incident audit events."""
    all_incidents = read_all_incidents()

    filtered = all_incidents
    if threat_category:
        norm_cat = threat_category.strip().upper()
        filtered = [inc for inc in filtered if inc.threat_category.upper() == norm_cat]

    if requires_human_escalation is not None:
        filtered = [inc for inc in filtered if inc.requires_human_escalation == requires_human_escalation]

    if search:
        query = search.strip().lower()
        filtered = [
            inc for inc in filtered
            if query in inc.filename.lower()
            or query in inc.sha256_hash.lower()
            or query in inc.incident_id.lower()
        ]

    total_count = len(filtered)
    paged = filtered[offset : offset + limit]

    return IncidentListResponse(
        items=paged,
        total_count=total_count,
        limit=limit,
        offset=offset,
    )


def get_incident_by_id(incident_id: str) -> Optional[IncidentAuditLog]:
    """Retrieves a single incident audit record by its unique ID."""
    clean_id = incident_id.strip()
    for inc in read_all_incidents():
        if inc.incident_id.upper() == clean_id.upper():
            return inc
    return None


def get_incident_stats() -> IncidentStatsResponse:
    """Aggregates threat analytics and escalation metrics across all incidents."""
    incidents = read_all_incidents()
    total = len(incidents)
    if total == 0:
        return IncidentStatsResponse(
            total_incidents=0,
            escalated_incidents=0,
            escalation_rate_percentage=0.0,
            average_fake_probability=0.0,
            threat_breakdown=[],
        )

    escalated = sum(1 for inc in incidents if inc.requires_human_escalation)
    avg_fake = sum(inc.fake_probability for inc in incidents) / total

    category_counts: dict[str, int] = {}
    for inc in incidents:
        category_counts[inc.threat_category] = category_counts.get(inc.threat_category, 0) + 1

    threat_breakdown = [
        ThreatDistribution(
            category=cat,
            count=count,
            percentage=round((count / total) * 100.0, 1),
        )
        for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    return IncidentStatsResponse(
        total_incidents=total,
        escalated_incidents=escalated,
        escalation_rate_percentage=round((escalated / total) * 100.0, 1),
        average_fake_probability=round(avg_fake, 3),
        threat_breakdown=threat_breakdown,
    )


def export_incidents_to_csv() -> str:
    """Exports all security incident audit logs into CSV format."""
    incidents = read_all_incidents()
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Incident ID",
        "Timestamp",
        "Filename",
        "SHA-256 Hash",
        "Fake Probability",
        "Threat Category",
        "Requires Escalation",
        "Client Host",
    ])

    for inc in incidents:
        writer.writerow([
            inc.incident_id,
            inc.timestamp,
            inc.filename,
            inc.sha256_hash,
            f"{inc.fake_probability:.4f}",
            inc.threat_category,
            "YES" if inc.requires_human_escalation else "NO",
            inc.client_host or "N/A",
        ])

    return output.getvalue()
