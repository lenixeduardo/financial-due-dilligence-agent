# Roadmap and maturity

## Delivered foundation
- Exact Decimal ratio operations, metadata compatibility guards and unit tests.
- SQL migration for workspaces and provenance-bearing evidence.
- Fail-closed single-workspace API key helper (not wired to endpoints yet).
- Deterministic isolated lexical retrieval with citation IDs (not vector RAG).
- Citations are tagged requires_verification; never represented as verified automatically.

## Pending in order
1. Provision PostgreSQL; run migrations in integration tests; implement parameterized repository queries.
2. Replace single-workspace key with identity provider and authorization (RLS / tenant boundaries); enforce on all routes.
3. Integrate licensed official sources using allowlisted egress, SSRF guards, rate limits and retry; immutable raw document storage and safe file parsing.
4. Hybrid vector + keyword retrieval using pgvector with scoped filters and evaluation dataset.
5. Add LLM adapter with strict structured output, prompt injection resistance and numeric/evidence claim verification.
6. Implement React FinSight UI (individual, sector, multissector) and report export with traced citations.
7. Security QA, dependency/secret scans, access tests, load tests and production deployment.

Do not expose publicly or call this production-ready.
