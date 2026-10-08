# RAG implementation boundary

Current implementation includes deterministic lexical retrieval, workspace filtering, evidence hashes, preliminary pgvector SQL, and a citation/quote validation contract.
**It is not yet a production RAG system** and there is no live embedding provider, vector index, hybrid retrieval or language model connected.

Before enabling:
1. License-review primary source feeds and harden network egress.
2. Parse verified documents in a sandbox; split into page-aware immutable chunks.
3. Assign and document embedding model/version and dimension; generate vectors in queued jobs.
4. Store workspace and company ACL metadata for every chunk. Enforce with database policies and application guards.
5. Add hybrid full-text and vector search, reranking, source version selection and citation disambiguation.
6. Evaluate precision, recall, faithfulness, prompt injection robustness and citation precision on a labeled test set.
7. A quote substring match is NOT semantic entailment. Human reviewers must approve substantive financial conclusions.
8. Never derive numeric financial facts from generated prose; use the deterministic financial calculation engine.
