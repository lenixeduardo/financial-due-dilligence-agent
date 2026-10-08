"""Versioned sector-aware financial methodology; input metrics must already be verified."""
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, model_validator

class Sector(str,Enum):
    BANK="bank"
    RETAIL="retail"
    SOFTWARE="software"
    INDUSTRIAL="industrial"

class Metric(str,Enum):
    ROE="roe"
    OPERATING_MARGIN="operating_margin"
    NET_DEBT_EBITDA="net_debt_ebitda"
    NONPERFORMING_LOANS="npl_ratio"
    RECURRING_REVENUE="recurring_revenue_ratio"

APPLICABLE={
    Metric.ROE:frozenset(Sector),
    Metric.OPERATING_MARGIN:frozenset({Sector.RETAIL,Sector.SOFTWARE,Sector.INDUSTRIAL}),
    Metric.NET_DEBT_EBITDA:frozenset({Sector.RETAIL,Sector.SOFTWARE,Sector.INDUSTRIAL}),
    Metric.NONPERFORMING_LOANS:frozenset({Sector.BANK}),
    Metric.RECURRING_REVENUE:frozenset({Sector.SOFTWARE}),
}

class Observation(BaseModel):
    company_id:str=Field(min_length=1)
    sector:Sector
    metric:Metric
    period:str=Field(pattern=r"^\d{4}-(?:FY|Q[1-4])$")
    value:Decimal
    source_ids:list[str]=Field(min_length=1)
    formula_version:str=Field(min_length=1)

    @model_validator(mode="after")
    def validate_applicability(self):
        if not self.value.is_finite() or self.sector not in APPLICABLE[self.metric]:
            raise ValueError("metric not applicable to this sector or invalid numeric value")
        return self

def compare(observations:list[Observation])->dict:
    if len(observations)<2:
        raise ValueError("at least two observations required")
    first=observations[0]
    if any((v.metric,v.period,v.formula_version)!=(first.metric,first.period,first.formula_version) for v in observations):
        raise ValueError("incompatible metric, period or formula")
    sectors={v.sector for v in observations}
    return {"metric":first.metric.value,"period":first.period,
      "comparison_type":"sector" if len(sectors)==1 else "cross_sector",
      "methodology":first.formula_version,"ranked":False,
      "results":[{"company_id":x.company_id,"sector":x.sector.value,"value":str(x.value),
                  "source_ids":x.source_ids} for x in observations]}
