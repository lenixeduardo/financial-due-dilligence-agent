from app.grounding import Citation, Interpretation, validate_interpretation
from app.evidence import Evidence

def evidence(workspace="one"):
    return Evidence.create(id="dfp-001",workspace_id=workspace,company_id="apple",
        source_url="https://example.org/dfp",publisher="Official issuer",
        document_version="2025",page=17,text="Net revenue in FY2025 was 50 million.")

def test_exact_quote_and_accessible_evidence_for_review():
    candidate=Interpretation(company_id="apple",narrative="Receita declarada.",citations=[
        Citation(evidence_id="dfp-001",quoted_text="Net revenue in FY2025 was 50 million.")])
    result=validate_interpretation(candidate,[evidence()],"one")
    assert result["accepted_for_review"] is True
    assert result["status"]=="requires_human_review"

def test_hallucinated_quote_rejected():
    candidate=Interpretation(company_id="apple",narrative="Receita de 100 milhões.",citations=[
        Citation(evidence_id="dfp-001",quoted_text="Net revenue was 100 million.")])
    assert validate_interpretation(candidate,[evidence()],"one")["status"]=="unsupported"

def test_cross_workspace_citation_rejected():
    candidate=Interpretation(company_id="apple",narrative="Text.",citations=[
        Citation(evidence_id="dfp-001",quoted_text="Net revenue in FY2025 was 50 million.")])
    assert validate_interpretation(candidate,[evidence()],"other")["status"]=="unsupported"
