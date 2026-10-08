BEGIN;
-- pgvector installed for future embedding-based retrieval; no embeddings created implicitly.
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS evidence_embeddings (
  evidence_id TEXT PRIMARY KEY REFERENCES evidence(id) ON DELETE CASCADE,
  workspace_id TEXT NOT NULL REFERENCES workspaces(id),
  model_id TEXT NOT NULL,
  embedding vector(384) NOT NULL,
  indexed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS evidence_embeddings_workspace_idx ON evidence_embeddings(workspace_id,model_id);
COMMIT;
