"""Grounded interpretation contracts. LLM outputs never become verified automatically."""
from decimal import Decimal
from pydantic import BaseModel, Field, model_validator
from .evidence import Evidence

class Citation(BaseModel):
    evidence_id: str = Field(min_length=1)
    quoted_text: str = Field(min_length=1,max_length=2000)

class Interpretation(BaseModel):
    company_id: str = Field(min_length=1)
    narrative: str = Field(min_length=1,max_length=5000)
    citations: list[Citation] = Field(min_length=1,max_length=30)
    status: str = "requires_human_review"

def validate_interpretation(candidate: Interpretation, evidence: list[Evidence], workspace_id: str) -> dict:
    """Check citation membership and exact quote presence. This is *not* entailment proof."""
    accessible = {e.id:e for e in evidence if e.workspace_id == workspace_id and e.company_id == candidate.company_id}
    errors=[]
    for cited in candidate.citations:
        document = accessible.get(cited.evidence_id)
        if document is None:
            errors.append(f"unknown or unauthorized evidence: {cited.evidence_id}")
        elif cited.quoted_text not in document.text:
            errors.append(f"quote not present: {cited.evidence_id}")
    return {"accepted_for_review": not errors, "status":"requires_human_review" if not errors else "unsupported",
            "errors":errors,"narrative":candidate.narrative if not errors else None}
