from pathlib import Path
import os
from uuid import uuid4
import pytest
from app.db import connection
from app.retrieval_db import search_chunks

pytestmark=pytest.mark.skipif(not os.environ.get("FINSIGHT_TEST_DATABASE_URL"),reason="ephemeral Postgres needed")

@pytest.fixture(autouse=True)
def database(monkeypatch):
    monkeypatch.setenv("FINSIGHT_DATABASE_URL",os.environ["FINSIGHT_TEST_DATABASE_URL"])
    with connection() as conn:
        for name in ["001_initial.sql","002_evidence_tenant_uniqueness.sql","003_retrieval_indexes.sql","004_searchable_chunks.sql"]:
            conn.execute((Path(__file__).resolve().parents[2]/"database"/name).read_text())
        conn.commit()

def test_full_text_isolated_by_workspace_and_company():
    w1,w2=["w"+uuid4().hex for _ in range(2)]
    evidences=["e"+uuid4().hex for _ in range(2)]
    chunks=["c"+uuid4().hex for _ in range(2)]
    with connection() as conn:
        for workspace in [w1,w2]:
            conn.execute("INSERT INTO workspaces(id,name) VALUES (%s,%s)",(workspace,workspace))
        for i,workspace in enumerate([w1,w2]):
            conn.execute("""INSERT INTO evidence(id,workspace_id,company_id,source_url,publisher,document_version,page,content_sha256,text_content)
                  VALUES (%s,%s,'apple','https://example.org/doc','Issuer','v1',1,%s,'cash flow increased')""",
                  (evidences[i],workspace,"a"*64))
            conn.execute("""INSERT INTO evidence_chunks(id,evidence_id,workspace_id,company_id,page,chunk_order,body)
                  VALUES (%s,%s,%s,'apple',1,0,'cash flow increased')""",
                  (chunks[i],evidences[i],workspace))
        conn.commit()
    hit=search_chunks(workspace_id=w1,company_id="apple",query="cash",limit=5)
    assert [x.chunk_id for x in hit if x.chunk_id in chunks]==[chunks[0]]
    assert search_chunks(workspace_id=w1,company_id="another",query="cash")==[]

def test_invalid_query_rejected():
    with pytest.raises(ValueError):
        search_chunks(workspace_id="w",company_id="c",query=" ")
