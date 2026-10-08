"""Structured evidence-bearing export; do not present as certified audit."""
import json
from datetime import datetime, timezone
from pydantic import BaseModel,Field
from .grounding import Interpretation

class AuditReport(BaseModel):
    report_id:str=Field(min_length=1)
    company_id:str=Field(min_length=1)
    methodology_version:str=Field(min_length=1)
    as_of_utc:datetime
    interpretation:Interpretation
    human_approved:bool=False

def export_report_json(report:AuditReport)->str:
    if report.human_approved and report.interpretation.status != "approved_by_reviewer":
        raise ValueError("human approval requires explicit reviewed interpretation")
    payload=report.model_dump(mode="json")
    payload["notice"]="Research assistance only. Not an audit opinion, independent appraisal or investment recommendation."
    return json.dumps(payload,ensure_ascii=False,sort_keys=True,indent=2)
