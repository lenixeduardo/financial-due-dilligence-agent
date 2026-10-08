"""Deterministic financial calculations; no LLM arithmetic."""
from decimal import Decimal, InvalidOperation
from typing import Literal
from pydantic import BaseModel, Field, field_validator, model_validator

Money = Decimal

class PeriodValue(BaseModel):
    period: str = Field(pattern=r"^\d{4}-(?:Q[1-4]|FY)$")
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    value: Money
    scope: Literal["consolidated", "standalone"]
    source_id: str = Field(min_length=1, max_length=128)
    @field_validator("value")
    @classmethod
    def finite(cls, value: Decimal) -> Decimal:
        if not value.is_finite():
            raise ValueError("non-finite financial number")
        return value

class RatioInputs(BaseModel):
    numerator: PeriodValue
    denominator: PeriodValue
    @model_validator(mode="after")
    def check_compatibility(self):
        x, y = self.numerator, self.denominator
        if (x.period, x.currency, x.scope) != (y.period, y.currency, y.scope):
            raise ValueError("period/currency/scope mismatch")
        if y.value == 0:
            raise ValueError("zero denominator")
        return self

class RatioResult(BaseModel):
    ratio: Decimal
    period: str
    currency: str
    scope: str
    evidence_ids: list[str]
    formula_version: str = "ratio-v1"

def calculate_ratio(data: RatioInputs) -> RatioResult:
    return RatioResult(
        ratio=data.numerator.value / data.denominator.value,
        period=data.numerator.period,
        currency=data.numerator.currency,
        scope=data.numerator.scope,
        evidence_ids=list(dict.fromkeys([data.numerator.source_id, data.denominator.source_id])),
    )

class SectorMetric(BaseModel):
    company_id: str = Field(min_length=1)
    sector: str = Field(min_length=1)
    metric_code: str = Field(min_length=1)
    methodology: str = Field(min_length=1)
    period: str
    value: Decimal
    @field_validator("value")
    @classmethod
    def finite(cls, value):
        if not value.is_finite():
            raise ValueError("non-finite metric")
        return value

def compare_metrics(metrics: list[SectorMetric], cross_sector: bool = False) -> list[SectorMetric]:
    if not metrics:
        raise ValueError("empty comparison")
    first = metrics[0]
    for metric in metrics[1:]:
        if (metric.metric_code, metric.methodology, metric.period) != (first.metric_code, first.methodology, first.period):
            raise ValueError("incompatible metrics")
        if metric.sector != first.sector and not cross_sector:
            raise ValueError("sector mismatch")
    # Cross-sector requires explicitly identical metric/methodology/period; no universal rank created.
    return metrics
