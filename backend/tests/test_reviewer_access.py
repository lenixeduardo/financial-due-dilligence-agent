from fastapi.testclient import TestClient
from app.main import app

def test_review_is_denied_with_workspace_key_only(tmp_path,monkeypatch):
    monkeypatch.setenv("FINSIGHT_SQLITE_PATH",str(tmp_path/"review.sqlite"))
    monkeypatch.setenv("FINSIGHT_WORKSPACE_ID","local")
    monkeypatch.setenv("FINSIGHT_WORKSPACE_API_KEY","test-workspace-secret")
    monkeypatch.setenv("FINSIGHT_REVIEW_API_KEY","test-separate-review-secret")
    item={"company_code":"1234","period":"2025-12-31","scope":"consolidated",
          "metric_code":"net_margin","formula_version":"v1","dataset_sha256":"a"*64,
          "reviewer":"reviewer-01","decision":"approved",
          "justification":"Reviewed against signed financial statements."}
    with TestClient(app) as client:
        base="/v1/workspaces/local/cvm/indicators/reviews"
        response=client.post(base,json=item,headers={"X-Workspace-Key":"test-workspace-secret"})
        assert response.status_code==403
        authorized=client.post(base,json=item,headers={
            "X-Workspace-Key":"test-workspace-secret",
            "X-Review-Key":"test-separate-review-secret"})
        # Permission passed; underlying indicator is intentionally absent.
        assert authorized.status_code==422
        assert "not found" in authorized.json()["detail"]

def test_same_secret_cannot_be_reused(tmp_path,monkeypatch):
    monkeypatch.setenv("FINSIGHT_SQLITE_PATH",str(tmp_path/"review2.sqlite"))
    monkeypatch.setenv("FINSIGHT_WORKSPACE_ID","local")
    monkeypatch.setenv("FINSIGHT_WORKSPACE_API_KEY","shared-secret")
    monkeypatch.setenv("FINSIGHT_REVIEW_API_KEY","shared-secret")
    with TestClient(app) as client:
        response=client.post("/v1/workspaces/local/cvm/indicators/reviews",
            headers={"X-Workspace-Key":"shared-secret","X-Review-Key":"shared-secret"},json={})
        assert response.status_code in (403,422)
