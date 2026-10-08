"""Single-origin, loopback-only Windows application (built React + FastAPI)."""
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .main import app as backend_api

def create_app(dist: str | Path | None = None) -> FastAPI:
    frontend = Path(dist or os.getenv("FINSIGHT_FRONTEND_DIST", "frontend/dist")).resolve()
    if not (frontend / "index.html").is_file():
        raise RuntimeError("Frontend build missing. Run npm run build in frontend/")
    site = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    site.mount("/api", backend_api)
    assets = frontend / "assets"
    if assets.is_dir():
        site.mount("/assets", StaticFiles(directory=str(assets)), name="assets")
    @site.get("/{path:path}", include_in_schema=False)
    def frontend_page(path: str):
        # Only serve the Vite build, never project files or private SQLite data.
        if path and ("/" not in path) and path in {"favicon.ico", "favicon.svg"}:
            target = frontend / path
            if target.is_file():
                return FileResponse(target)
        return FileResponse(frontend / "index.html", headers={
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
            "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; object-src 'none'; frame-ancestors 'none'",
        })
    return site

def serve():
    import uvicorn
    host = "127.0.0.1"  # Not accessible from other machines on the LAN.
    port = int(os.getenv("FINSIGHT_LOCAL_PORT", "8765"))
    if not 1024 <= port <= 65535:
        raise ValueError("invalid local port")
    uvicorn.run(create_app(), host=host, port=port, proxy_headers=False, access_log=False)

if __name__ == "__main__":
    serve()
