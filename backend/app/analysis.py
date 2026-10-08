"""Cited extractive answers. Never fabricate a claim absent verified sources."""
from pydantic import BaseModel, Field
from .retrieval_db import search_chunks

class EvidenceAnswer(BaseModel):
    question: str
    status: str
    passages: list[dict]
    interpretation: str | None = None

def answer_from_evidence(*, workspace_id: str, company_id: str, question: str,
                         max_passages: int = 5) -> EvidenceAnswer:
    if not question.strip() or len(question) > 500 or not 1 <= max_passages <= 10:
        raise ValueError("invalid question")
    hits = search_chunks(workspace_id=workspace_id,company_id=company_id,
                         query=question,limit=max_passages)
    return EvidenceAnswer(question=question,
        status="evidence_found_requires_review" if hits else "insufficient_evidence",
        passages=[{"evidence_id":hit.evidence_id,"source_url":hit.source_url,
                   "publisher":hit.publisher,"page":hit.page,
                   "excerpt":hit.snippet} for hit in hits],
        interpretation=None)
