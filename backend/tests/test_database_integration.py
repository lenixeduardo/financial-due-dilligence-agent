"""Runs against an ephemeral CI PostgreSQL database; never production."""
import os
from pathlib import Path
from uuid import uuid4
import pytest
from app.db import insert_evidence, list_evidence
from app.evidence import Evidence

pytestmark = pytest.mark.skipif(not os.getenv("FINSIGHT_TEST_DATABASE_URL"),reason="ephemeral test PostgreSQL required")

@pytest.fixture(autouse=True)
def configured_db(monkeypatch):
    monkeypatch.setenv("FINSIGHT_DATABASE_URL",os.environ["FINSIGHT_TEST_DATABASE_URL"])
    import psycopg
    with psycopg.connect(os.environ["FINSIGHT_TEST_DATABASE_URL"]) as conn:
        for filename in ["001_initial.sql","002_evidence_tenant_uniqueness.sql","003_retrieval_indexes.sql"]:
            sql=(Path(__file__).resolve().parents[2]/"database"/filename).read_text()
            conn.execute(sql)
        conn.commit()

def test_real_database_tenant_separation():
    import psycopg
    first="w-"+uuid4().hex
    second="w-"+uuid4().hex
    with psycopg.connect(os.environ["FINSIGHT_TEST_DATABASE_URL"]) as conn:
        conn.execute("INSERT INTO workspaces(id,name) VALUES (%s,%s),(%s,%s)",(first,"One",second,"Two"))
        conn.commit()
    evidence = Evidence.create(id=uuid4().hex,workspace_id=first,company_id="apple",
       source_url="https://www.gov.br/cvm/test",publisher="CVM",document_version="v1",
       page=1,text="Document evidence checked for tenant isolation.")
    insert_evidence(evidence)
    assert [e.id for e in list_evidence(first,"apple") if e.id==evidence.id]==[evidence.id]
    assert evidence.id not in [e.id for e in list_evidence(second,"apple")]
