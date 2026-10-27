import io
import pytest
from fastapi.testclient import TestClient
from main import app
from services.audit_logger import log_fraud_incident
from services.incident_service import _AUDIT_LOG_FILE


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_audit_log():
    """Ensure a clean audit log before and after tests."""
    backup = None
    if _AUDIT_LOG_FILE.exists():
        backup = _AUDIT_LOG_FILE.read_bytes()
        _AUDIT_LOG_FILE.unlink()
    yield
    if backup is not None:
        _AUDIT_LOG_FILE.write_bytes(backup)
    elif _AUDIT_LOG_FILE.exists():
        _AUDIT_LOG_FILE.unlink()


def test_list_incidents_empty(client):
    response = client.get("/api/v1/incidents")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total_count"] == 0


def test_list_and_filter_incidents(client):
    # Seed sample incidents
    inc1 = log_fraud_incident(
        filename="ceo_voice_clone.wav",
        sha256_hash="1111" * 16,
        fake_probability=0.92,
        threat_category="CRITICAL_VOICE_CLONING_FRAUD",
        requires_human_escalation=True,
    )
    inc2 = log_fraud_incident(
        filename="customer_kyc_sample.wav",
        sha256_hash="2222" * 16,
        fake_probability=0.15,
        threat_category="AUTHENTIC_HUMAN_SPEECH",
        requires_human_escalation=False,
    )

    # All incidents
    resp = client.get("/api/v1/incidents")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_count"] == 2
    assert len(body["items"]) == 2

    # Filter by category
    resp_cat = client.get("/api/v1/incidents?threat_category=CRITICAL_VOICE_CLONING_FRAUD")
    assert resp_cat.status_code == 200
    assert resp_cat.json()["total_count"] == 1
    assert resp_cat.json()["items"][0]["incident_id"] == inc1.incident_id

    # Filter by escalation
    resp_esc = client.get("/api/v1/incidents?requires_human_escalation=false")
    assert resp_esc.status_code == 200
    assert resp_esc.json()["total_count"] == 1
    assert resp_esc.json()["items"][0]["incident_id"] == inc2.incident_id

    # Search keyword
    resp_search = client.get("/api/v1/incidents?search=ceo_voice")
    assert resp_search.status_code == 200
    assert resp_search.json()["total_count"] == 1
    assert resp_search.json()["items"][0]["filename"] == "ceo_voice_clone.wav"


def test_get_incident_by_id(client):
    inc = log_fraud_incident(
        filename="sample.wav",
        sha256_hash="aaaa" * 16,
        fake_probability=0.75,
        threat_category="SUSPECTED_VOICE_SYNTHESIS",
        requires_human_escalation=True,
    )

    resp = client.get(f"/api/v1/incidents/{inc.incident_id}")
    assert resp.status_code == 200
    assert resp.json()["incident_id"] == inc.incident_id
    assert resp.json()["threat_category"] == "SUSPECTED_VOICE_SYNTHESIS"

    # Non-existent ID
    resp_missing = client.get("/api/v1/incidents/INC-NONEXISTENT")
    assert resp_missing.status_code == 404
    assert "not found" in resp_missing.json()["detail"].lower()


def test_incident_stats(client):
    log_fraud_incident(
        filename="test1.wav",
        sha256_hash="1111" * 16,
        fake_probability=0.8,
        threat_category="CRITICAL_VOICE_CLONING_FRAUD",
        requires_human_escalation=True,
    )
    log_fraud_incident(
        filename="test2.wav",
        sha256_hash="2222" * 16,
        fake_probability=0.2,
        threat_category="AUTHENTIC_HUMAN_SPEECH",
        requires_human_escalation=False,
    )

    resp = client.get("/api/v1/incidents/stats")
    assert resp.status_code == 200
    stats = resp.json()
    assert stats["total_incidents"] == 2
    assert stats["escalated_incidents"] == 1
    assert stats["escalation_rate_percentage"] == 50.0
    assert stats["average_fake_probability"] == 0.5
    assert len(stats["threat_breakdown"]) == 2


def test_export_csv(client):
    log_fraud_incident(
        filename="export_sample.wav",
        sha256_hash="9999" * 16,
        fake_probability=0.88,
        threat_category="CRITICAL_VOICE_CLONING_FRAUD",
        requires_human_escalation=True,
    )

    resp = client.get("/api/v1/incidents/export/csv")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    csv_text = resp.text
    assert "Incident ID,Timestamp,Filename,SHA-256 Hash" in csv_text
    assert "export_sample.wav" in csv_text
    assert "CRITICAL_VOICE_CLONING_FRAUD" in csv_text
