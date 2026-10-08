from decimal import Decimal
import pytest
from pydantic import ValidationError
from app.methodologies import Observation,compare

def observation(company,sector="software",metric="operating_margin",version="v1"):
    return Observation(company_id=company,sector=sector,metric=metric,period="2025-FY",
        value=Decimal("12.5"),source_ids=["filing-1"],formula_version=version)

def test_sector_comparison():
    r=compare([observation("a"),observation("b")])
    assert r["comparison_type"]=="sector"
    assert not r["ranked"]

def test_cross_sector_comparison_not_ranked():
    r=compare([observation("a"),observation("b","retail")])
    assert r["comparison_type"]=="cross_sector"
    assert r["ranked"] is False

def test_bank_debt_ebitda_rejected():
    with pytest.raises(ValidationError):
        observation("bank-a","bank","net_debt_ebitda")

def test_different_methodology_rejected():
    with pytest.raises(ValueError):
        compare([observation("a"),observation("b",version="v2")])

def test_nonfinite_rejected():
    with pytest.raises(ValidationError):
        Observation(company_id="a",sector="software",metric="roe",period="2025-FY",
                    value=Decimal("NaN"),source_ids=["doc"],formula_version="v1")
