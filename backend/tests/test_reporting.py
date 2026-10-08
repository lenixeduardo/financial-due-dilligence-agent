import json
from datetime import datetime,timezone
import pytest
from app.grounding import Interpretation,Citation
from app.reporting import AuditReport,export_report_json

def report(approved=False):
    return AuditReport(report_id="r1",company_id="a",methodology_version="v1",
      as_of_utc=datetime(2026,10,8,tzinfo=timezone.utc),
      interpretation=Interpretation(company_id="a",narrative="Hypothesis",citations=[
          Citation(evidence_id="e1",quoted_text="Exact evidence")]),
      human_approved=approved)

def test_export_includes_notice_and_citations():
    payload=json.loads(export_report_json(report()))
    assert payload["interpretation"]["citations"][0]["evidence_id"]=="e1"
    assert "Not an audit opinion" in payload["notice"]

def test_claimed_approval_without_review_rejected():
    with pytest.raises(ValueError):
        export_report_json(report(True))
