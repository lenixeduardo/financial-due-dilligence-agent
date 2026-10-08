"""Evidence retrieval foundation with source grounding and tenant boundaries."""
from dataclasses import dataclass
from hashlib import sha256
from typing import Sequence

@dataclass(frozen=True)
class Evidence:
    id: str
    workspace_id: str
    company_id: str
    source_url: str
    publisher: str
    document_version: str
    page: int
    text: str
    sha256_hex: str

    @staticmethod
    def create(*, id: str, workspace_id: str, company_id: str, source_url: str, publisher: str, document_version: str, page: int, text: str):
        if not id or not workspace_id or not company_id or not publisher or not document_version or page < 1 or not text.strip():
            raise ValueError("missing evidence provenance")
        if not source_url.startswith("https://"):
            raise ValueError("non-HTTPS evidence URL")
        return Evidence(id, workspace_id, company_id, source_url, publisher, document_version, page, text,
                        sha256(text.encode("utf-8")).hexdigest())

@dataclass(frozen=True)
class Finding:
    claim: str
    evidence_ids: tuple[str, ...]
    status: str

def retrieve(query: str, *, workspace_id: str, company_id: str, documents: Sequence[Evidence], limit: int = 5) -> list[Evidence]:
    """Deterministic lexical baseline, not semantic RAG. Must not leak across workspaces."""
    if not query.strip() or not workspace_id or not company_id or not 1 <= limit <= 20:
        raise ValueError("invalid retrieval request")
    terms = set(query.lower().split())
    matches = [e for e in documents if e.workspace_id == workspace_id and e.company_id == company_id]
    return sorted(matches, key=lambda e: (-len(terms.intersection(e.text.lower().split())), e.id))[:limit]

def support_claim(claim: str, evidence_ids: Sequence[str], *, workspace_id: str, company_id: str, documents: Sequence[Evidence]) -> Finding:
    """Presence of a citation is not proof of semantic entailment. Return for human review."""
    allowed = {e.id for e in documents if e.workspace_id == workspace_id and e.company_id == company_id}
    if not claim.strip():
        raise ValueError("empty claim")
    if not evidence_ids or any(eid not in allowed for eid in evidence_ids):
        return Finding(claim, tuple(), "unsupported")
    return Finding(claim, tuple(dict.fromkeys(evidence_ids)), "requires_verification")
