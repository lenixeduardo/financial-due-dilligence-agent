# Connected local workbench

1. Create a venv; install `backend/requirements.txt`.
2. Set environment: `FINSIGHT_SQLITE_PATH=data/finsight.sqlite3`, `FINSIGHT_WORKSPACE_ID=local` and a strong random `FINSIGHT_WORKSPACE_API_KEY`.
3. Run `uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000`.
4. In `frontend/`, run `npm install` and `npm run dev`.
5. Open the local Vite URL, select individual analysis, and supply workspace, API key, company identifier, issuer, source HTTPS URL, version and a locally authorized document.
6. Import PDF/TXT/CSV; then search for keywords. Indexed passages carry source metadata and always require manual verification.

The key is transient browser state (never localStorage). Vite proxies `/api` to the local backend only. No production authentication system is supplied. Never deploy this development frontend or proxy publicly. PDF parsing is not sandboxed against hostile documents. Uploads are limited to 8 MB and 100 PDF pages.

Known gap: sectoral and multi-sector UI remain conceptual; the connected workbench supports evidence search for a single company only.
