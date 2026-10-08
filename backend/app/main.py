"""FinSight API foundation: no file uploads, network fetch or LLM invocation."""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError
from .finance import RatioInputs, RatioResult, calculate_ratio, SectorMetric, compare_metrics

app = FastAPI(title="FinSight", version="0.1.0", docs_url="/docs", redoc_url=None)

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
    metrics: list[SectorMetric] = Field(min_length=2, max_length=100)
    cross_sector: bool = False

@app.post("/v1/metrics/validate-comparison")
def validate_comparison(payload: ComparisonInput):
    try:
        checked = compare_metrics(payload.metrics, payload.cross_sector)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return {"comparable": True, "metric_code": checked[0].metric_code, "companies": len(checked),
            "cross_sector": payload.cross_sector, "rank_generated": False}
