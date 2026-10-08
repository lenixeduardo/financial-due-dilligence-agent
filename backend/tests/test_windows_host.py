from fastapi.testclient import TestClient
from app.windows_host import create_app

def test_local_windows_frontend_and_api(tmp_path,monkeypatch):
    folder=tmp_path/"dist"; folder.mkdir()
    (folder/"index.html").write_text("<h1>FinSight offline</h1>",encoding="utf-8")
    monkeypatch.setenv("FINSIGHT_SQLITE_PATH",str(tmp_path/"db.sqlite"))
    monkeypatch.setenv("FINSIGHT_AUTH_MODE","users")
    monkeypatch.setenv("FINSIGHT_WORKSPACE_ID","local")
    with TestClient(create_app(folder)) as client:
        assert client.get("/").status_code==200
        assert "FinSight offline" in client.get("/").text
        assert client.get("/api/health").status_code==200
        assert client.get("/nonexistent/spa/route").status_code==200
        assert client.get("/api/v1/workspaces/local/cvm/1234/indicators").status_code==401

def test_missing_frontend_build_refused(tmp_path):
    import pytest
    with pytest.raises(RuntimeError):
        create_app(tmp_path)
