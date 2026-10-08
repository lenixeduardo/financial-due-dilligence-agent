from dataclasses import replace
from decimal import Decimal
import sqlite3
import pytest
from app.db import initialize_database,ensure_workspace,connection
from app.cvm_indicators import CalculatedIndicator
from app.indicator_store import persist_indicators
from app.indicator_review import review_indicator,list_reviews

def seeded(tmp_path,monkeypatch):
    monkeypatch.setenv("FINSIGHT_SQLITE_PATH",str(tmp_path/"fin.sqlite"))
    initialize_database()
    ensure_workspace("one");ensure_workspace("two")
    item=CalculatedIndicator(metric_code="net_margin",company_code="1234",
        period="2025-12-31",scope="consolidated",value=Decimal("0.2"),unit="ratio",
        formula_version="cvm-basic-v1",source_sha256="a"*64,account_codes=("3.11","3.01"))
    persist_indicators("one",[item])
    return dict(workspace_id="one",company_code="1234",period=item.period,
      scope=item.scope,metric_code=item.metric_code,formula_version=item.formula_version,
      dataset_sha256=item.source_sha256,reviewer="reviewer-01",justification="Compared with the official filing figures.")

def test_append_only_review_history(tmp_path,monkeypatch):
    kwargs=seeded(tmp_path,monkeypatch)
    first=review_indicator(**kwargs,decision="rejected")
    second=review_indicator(**{**kwargs,"justification":"Second review completed against the published DFP."},decision="approved")
    assert first["event_id"]<second["event_id"]
    events=list_reviews("one","1234")
    assert [r["decision"] for r in events]==["approved","rejected"]
    assert events[0]["prev_hash"]==events[1]["event_hash"]
    with connection() as db:
        with pytest.raises(sqlite3.DatabaseError):
            db.execute("DELETE FROM indicator_reviews")

def test_tenant_isolation_and_required_justification(tmp_path,monkeypatch):
    data=seeded(tmp_path,monkeypatch)
    with pytest.raises(ValueError):
        review_indicator(**{**data,"workspace_id":"two"},decision="approved")
    with pytest.raises(ValueError):
        review_indicator(**{**data,"justification":"ok"},decision="approved")
    assert list_reviews("two","1234")==[]
