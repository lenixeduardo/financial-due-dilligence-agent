# Hybrid retrieval
`hybrid_search` combines normalized cosine similarity with lexical relevance, restricted by workspace, company and embedding model ID. The initial 0.4/0.6 weighting is provisional and must be tuned on a labeled evaluation dataset.

**Requires** a real 384-dimensional embedding model and an ingestion worker populating `chunk_embeddings`. Nothing automatically generates vectors, and without embeddings the hybrid query returns no results. Do not present it as live RAG until deployment and evaluation.
