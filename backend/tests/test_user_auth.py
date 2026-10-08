import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import initialize_database,ensure_workspace
from app.user_auth import create_user,authenticate,lookup_session,revoke_token

def seeded(tmp_path,monkeypatch):
    monkeypatch.setenv("FINSIGHT_SQLITE_PATH",str(tmp_path/"auth.sqlite"))
    monkeypatch.setenv("FINSIGHT_AUTH_MODE","users")
    initialize_database()
    ensure_workspace("one");ensure_workspace("two")
    create_user(workspace_id="one",username="reviewer_01",password="high-entropy-test-password",role="reviewer")

def test_sqlite_user_sessions_and_isolation(tmp_path,monkeypatch):
    seeded(tmp_path,monkeypatch)
    assert authenticate(workspace_id="one",username="reviewer_01",password="wrong") is None
    token=authenticate(workspace_id="one",username="reviewer_01",password="high-entropy-test-password")
    assert token and lookup_session(token,"one")["role"]=="reviewer"
    assert lookup_session(token,"two") is None
    revoke_token(token)
    assert lookup_session(token,"one") is None

def test_api_sign_in_and_cross_workspace_denial(tmp_path,monkeypatch):
    seeded(tmp_path,monkeypatch)
    with TestClient(app) as client:
        r=client.post("/v1/auth/login",json={"workspace_id":"one","username":"reviewer_01","password":"high-entropy-test-password"})
        assert r.status_code==200,r.text
        token=r.json()["access_token"]
        assert client.get("/v1/auth/me",params={"workspace_id":"one"},
          headers={"Authorization":"Bearer "+token}).json()["role"]=="reviewer"
        assert client.get("/v1/auth/me",params={"workspace_id":"two"},
          headers={"Authorization":"Bearer "+token}).status_code==401
        assert client.post("/v1/auth/logout",headers={"Authorization":"Bearer "+token}).status_code==200

def test_bad_password_or_short_account_rejected(tmp_path,monkeypatch):
    seeded(tmp_path,monkeypatch)
    with pytest.raises(ValueError):
        create_user(workspace_id="one",username="bad",password="weak",role="reader")
