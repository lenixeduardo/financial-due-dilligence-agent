"""FinSight API: deterministic calculations and protected evidence access."""
from fastapi import FastAPI, HTTPException, Request
from contextlib import asynccontextmanager
import os
from .db import initialize_database, ensure_workspace
from pydantic import BaseModel, Field
from .finance import RatioInputs, RatioResult, calculate_ratio, SectorMetric, compare_metrics
from .evidence_api import router as evidence_router
from .ingestion_api import router as ingestion_router
from .comparison_api import router as comparison_router
from .cvm_api import router as cvm_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    workspace = os.getenv("FINSIGHT_WORKSPACE_ID")
    if workspace:
        ensure_workspace(workspace)
    yield

app = FastAPI(title="FinSight", version="0.3.0", docs_url="/docs", redoc_url=None, lifespan=lifespan)
app.include_router(evidence_router)
app.include_router(ingestion_router)
app.include_router(comparison_router)
app.include_router(cvm_router)

@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    return response

@app.get("/health")
def health():
    return {"status": "ok", "service": "finsight"}

@app.post("/v1/metrics/ratio", response_model=RatioResult)
def ratio(payload: RatioInputs):
    return calculate_ratio(payload)

class ComparisonInput(BaseModel):
    metrics: list[SectorMetric] = Field(min_length=2,max_length=100)
    cross_sector: bool = False

@app.post("/v1/metrics/validate-comparison")
def validate_comparison(payload: ComparisonInput):
    try:
        checked = compare_metrics(payload.metrics,payload.cross_sector)
    except ValueError as exc:
        raise HTTPException(status_code=422,detail=str(exc))
    return {"comparable":True,"metric_code":checked[0].metric_code,"companies":len(checked),
            "cross_sector":payload.cross_sector,"rank_generated":False}
