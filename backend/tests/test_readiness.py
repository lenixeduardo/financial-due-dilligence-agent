from fastapi.testclient import TestClient
from app.main import app
from app.db import initialize_database,ensure_workspace

def test_production_requires_session_auth_and_durable_path(tmp_path,monkeypatch):
    filename=tmp_path/"state.sqlite"
    monkeypatch.setenv("FINSIGHT_SQLITE_PATH",str(filename))
    monkeypatch.setenv("FINSIGHT_WORKSPACE_ID","local")
    monkeypatch.setenv("FINSIGHT_ENV","production")
    monkeypatch.setenv("FINSIGHT_AUTH_MODE","keys")
    with TestClient(app) as client:
        assert client.get("/ready").status_code==503
    monkeypatch.setenv("FINSIGHT_AUTH_MODE","users")
    with TestClient(app) as client:
        assert client.get("/ready").status_code==503  # /tmp is forbidden for production data
        assert client.get("/health").status_code==200
    monkeypatch.setenv("FINSIGHT_ENV","development")
    with TestClient(app) as client:
        assert client.get("/ready").status_code==200
