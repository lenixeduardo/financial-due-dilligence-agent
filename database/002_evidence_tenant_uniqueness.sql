BEGIN;
-- Idempotent migration for repeated integration test setups.
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'evidence_workspace_id_unique') THEN
    ALTER TABLE evidence ADD CONSTRAINT evidence_workspace_id_unique UNIQUE (workspace_id,id);
  END IF;
END;
$$;
CREATE INDEX IF NOT EXISTS evidence_tenant_latest_idx ON evidence(workspace_id,company_id,created_at DESC);
COMMIT;
