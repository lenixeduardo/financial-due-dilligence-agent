from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from app.finance import PeriodValue, RatioInputs, calculate_ratio, SectorMetric, compare_metrics
from app.main import app

def p(value, period="2025-FY", currency="BRL", scope="consolidated", source="document-1"):
    return PeriodValue(value=Decimal(value), period=period, currency=currency, scope=scope, source_id=source)

def test_exact_decimal_ratio_with_evidence():
    result = calculate_ratio(RatioInputs(numerator=p("0.3", source="dfp-1"), denominator=p("0.1", source="dfp-2")))
    assert result.ratio == Decimal("3")
    assert result.evidence_ids == ["dfp-1", "dfp-2"]

@pytest.mark.parametrize("change", [{"period":"2024-FY"}, {"currency":"USD"}, {"scope":"standalone"}])
def test_incompatible_input_rejected(change):
    with pytest.raises(ValidationError):
        RatioInputs(numerator=p("10"), denominator=p("2", **change))

def test_zero_denominator_rejected():
    with pytest.raises(ValidationError):
        RatioInputs(numerator=p("10"), denominator=p("0"))

@pytest.mark.parametrize("bad", ["NaN", "Infinity", "-Infinity"])
def test_nonfinite_rejected(bad):
    with pytest.raises(ValidationError):
        p(bad)

def metric(company, sector, name="ROIC", method="roic-v1"):
    return SectorMetric(company_id=company, sector=sector, metric_code=name,
                        methodology=method, period="2025-FY", value=Decimal("12.4"))

def test_sector_mismatch_rejected():
    with pytest.raises(ValueError):
        compare_metrics([metric("a","bank"), metric("b","retail")])

def test_cross_sector_same_methodology_allowed_without_rank():
    assert len(compare_metrics([metric("a","retail"), metric("b","technology")],cross_sector=True)) == 2

def test_cross_sector_incompatible_metric_rejected():
    with pytest.raises(ValueError):
        compare_metrics([metric("a","bank"), metric("b","retail",name="ROE")],cross_sector=True)

def test_api_and_headers():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["cache-control"] == "no-store"
    response = client.post("/v1/metrics/ratio",json={"numerator":p("10").model_dump(mode="json"),
                                                      "denominator":p("2").model_dump(mode="json")})
    assert response.status_code == 200
    assert response.json()["ratio"] == "5"
