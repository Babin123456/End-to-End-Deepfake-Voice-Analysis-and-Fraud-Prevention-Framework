from fastapi.testclient import TestClient

from core.config import get_settings


def load_settings(monkeypatch, **env):
    for name in ("CORS_ORIGINS", "FRONTEND_ORIGIN", "MAX_UPLOAD_SIZE", "UPLOAD_CHUNK_SIZE"):
        monkeypatch.delenv(name, raising=False)
    for name, value in env.items():
        monkeypatch.setenv(name, value)
    get_settings.cache_clear()
    return get_settings()


def test_defaults_match_old_hardcoded_values(monkeypatch):
    settings = load_settings(monkeypatch)
    assert settings.cors_origins == ["http://localhost:3000", "http://127.0.0.1:3000"]
    assert settings.max_upload_size == 25 * 1024 * 1024
    assert settings.upload_chunk_size == 1024 * 1024


def test_cors_origins_comma_separated(monkeypatch):
    settings = load_settings(
        monkeypatch, CORS_ORIGINS="https://a.example.com/, https://b.example.com ,"
    )
    assert settings.cors_origins == ["https://a.example.com", "https://b.example.com"]


def test_frontend_origin_fallback(monkeypatch):
    settings = load_settings(monkeypatch, FRONTEND_ORIGIN="https://app.example.com/")
    assert settings.cors_origins[-1] == "https://app.example.com"
    assert "http://localhost:3000" in settings.cors_origins


def test_frontend_origin_not_duplicated(monkeypatch):
    settings = load_settings(
        monkeypatch,
        CORS_ORIGINS="https://app.example.com",
        FRONTEND_ORIGIN="https://app.example.com",
    )
    assert settings.cors_origins == ["https://app.example.com"]


def test_get_settings_is_cached(monkeypatch):
    first = load_settings(monkeypatch)
    assert get_settings() is first


def test_health_route(monkeypatch):
    load_settings(monkeypatch)
    from main import app

    response = TestClient(app).get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["uptime_seconds"] >= 0
    assert body["python_version"]
    assert body["platform"]
    assert body["upload_limits"] == {
        "max_upload_size": 25 * 1024 * 1024,
        "upload_chunk_size": 1024 * 1024,
    }
