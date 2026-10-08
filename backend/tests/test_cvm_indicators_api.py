import base64
from io import BytesIO
from zipfile import ZipFile
from fastapi.testclient import TestClient
from app.main import app

def make_zip():
    buf=BytesIO()
    head="CD_CVM;DT_REFER;CD_CONTA;DS_CONTA;VL_CONTA;ORDEM_EXERC;ESCALA_MOEDA;VERSAO\n"
    lines="1234;2025-12-31;3.01;Revenue;200;ÚLTIMO;MIL;1\n1234;2025-12-31;3.05;Operating;40;ÚLTIMO;MIL;1\n1234;2025-12-31;3.11;Profit;20;ÚLTIMO;MIL;1\n"
    with ZipFile(buf,"w") as z:
        z.writestr("dfp_cia_aberta_DRE_con_2025.csv",(head+lines).encode())
    return base64.b64encode(buf.getvalue()).decode()

def test_ingest_ratio_and_scoped_read(tmp_path,monkeypatch):
    monkeypatch.setenv("FINSIGHT_SQLITE_PATH",str(tmp_path/"finance.sqlite"))
    monkeypatch.setenv("FINSIGHT_WORKSPACE_ID","local")
    monkeypatch.setenv("FINSIGHT_WORKSPACE_API_KEY","test-secret")
    h={"X-Workspace-Key":"test-secret"}
    with TestClient(app) as c:
        payload={"company_code":"1234","year":2025,"zip_base64":make_zip()}
        assert c.post("/v1/workspaces/local/cvm/dfp/indicators",json=payload).status_code==403
        r=c.post("/v1/workspaces/local/cvm/dfp/indicators",json=payload,headers=h)
        assert r.status_code==200,r.text
        assert {x["metric_code"]:x["value"] for x in r.json()["computed"]}=={
            "operating_margin":"0.2","net_margin":"0.1"}
        results=c.get("/v1/workspaces/local/cvm/1234/indicators",headers=h)
        assert results.status_code==200
        assert len(results.json()["indicators"])==2
        assert c.get("/v1/workspaces/other/cvm/1234/indicators",headers=h).status_code==403
        assert c.post("/v1/workspaces/local/cvm/dfp/indicators",json=payload,headers=h).json()["stored"]==0
