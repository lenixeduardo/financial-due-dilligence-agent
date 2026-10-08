# FinSight SQLite — single-machine deployment

No Supabase license or PostgreSQL server is required.

1. Set `FINSIGHT_SQLITE_PATH` to a private persistent location, e.g. `data/finsight.sqlite3`.
2. Initialize once using `PYTHONPATH=backend python -c "from app.db import initialize_database; initialize_database()"`.
3. Set single-workspace secrets with `FINSIGHT_WORKSPACE_ID` and `FINSIGHT_WORKSPACE_API_KEY` in environment variables.
4. Start the backend: `uvicorn app.main:app --app-dir backend --host 127.0.0.1`.
5. Run tests: `PYTHONPATH=backend pytest -q backend/tests`.

SQLite uses foreign keys, busy timeout, WAL and SQLite FTS5. Semantic retrieval uses 384-d vectors stored as JSON with bounded Python cosine evaluation; **this is appropriate only for small local corpora**, not distributed high-throughput deployments. Real embeddings must still be generated separately. No LLM, authorized external source ingestion, certified financial judgments or full identity system is supplied by this migration.

Security: protect the DB file and -wal/-shm sidecars, back up through the SQLite backup API, restrict filesystem permissions and never place the database under static web directories or commit it. The shared workspace key is not a substitute for production login/RBAC.
