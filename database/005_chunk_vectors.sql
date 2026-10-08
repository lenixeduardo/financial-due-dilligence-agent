BEGIN;
CREATE TABLE IF NOT EXISTS chunk_embeddings (
 chunk_id TEXT NOT NULL REFERENCES evidence_chunks(id) ON DELETE CASCADE,
 workspace_id TEXT NOT NULL REFERENCES workspaces(id),
 model_id TEXT NOT NULL,
 embedding vector(384) NOT NULL,
 indexed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 PRIMARY KEY(chunk_id,model_id)
);
CREATE INDEX IF NOT EXISTS chunk_embeddings_scope ON chunk_embeddings(workspace_id,model_id);
-- HNSW indexing is optional for small installations; benchmark before enabling.
COMMIT;
