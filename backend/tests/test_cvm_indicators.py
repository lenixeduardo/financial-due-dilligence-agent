from dataclasses import replace
from decimal import Decimal
import pytest
from app.cvm_statements import AccountingLine
from app.cvm_indicators import calculate_indicators
from app.indicator_store import persist_indicators,get_indicators
from app.db import initialize_database,ensure_workspace

def line(statement,code,value,scale="MIL"):
    return AccountingLine(source_file="dfp_test.csv",dataset_sha256="a"*64,
      document_type="dfp",statement=statement,scope="consolidated",archive_year=2025,
      cvm_code="1234",reference_date="2025-12-31",account_code=code,
      account_description="mock",financial_value=Decimal(value),currency_scale=scale,
      presentation_order="ÚLTIMO",reporting_version="1")

def sample():
    return [line("DRE","3.01","200"),line("DRE","3.05","40"),
            line("DRE","3.11","20"),line("BPA","1.01","300"),
            line("BPP","2.01","150")]

def test_exact_accounting_ratios():
    indicators={r.metric_code:r for r in calculate_indicators(sample())}
    assert indicators["operating_margin"].value==Decimal("0.2")
    assert indicators["net_margin"].value==Decimal("0.1")
    assert indicators["current_ratio"].value==Decimal("2")
    assert all(v.status=="requires_source_review" for v in indicators.values())

def test_mixed_scope_rejected():
    with pytest.raises(ValueError):
        calculate_indicators(sample()+[replace(line("DRE","3.01","200"),scope="standalone")])

def test_duplicate_line_rejected():
    with pytest.raises(ValueError):
        calculate_indicators(sample()+[line("DRE","3.01","250")])

def test_no_division_by_zero():
    altered=[replace(v,financial_value=Decimal("0")) if v.account_code=="3.01" else v for v in sample()]
    assert not any(x.metric_code in ("operating_margin","net_margin") for x in calculate_indicators(altered))

def test_sqlite_roundtrip(tmp_path,monkeypatch):
    monkeypatch.setenv("FINSIGHT_SQLITE_PATH",str(tmp_path/"finsight.sqlite"))
    initialize_database()
    ensure_workspace("one");ensure_workspace("two")
    indicators=calculate_indicators(sample())
    assert persist_indicators("one",indicators)==3
    assert persist_indicators("one",indicators)==0
    assert len(get_indicators("one","1234"))==3
    assert get_indicators("two","1234")==[]
