"""Conservative deterministic CVM indicators; never infer missing accounting lines."""
from dataclasses import dataclass
from decimal import Decimal
from .cvm_statements import AccountingLine, SCALES

# DRE/BPA/BPP account mappings: issuer-specific mapping must be reviewed before production.
ACCOUNTS={
    "net_revenue":("DRE","3.01"),
    "operating_result":("DRE","3.05"),
    "net_income":("DRE","3.11"),
    "current_assets":("BPA","1.01"),
    "current_liabilities":("BPP","2.01"),
}
RATIOS={
    "operating_margin":("operating_result","net_revenue"),
    "net_margin":("net_income","net_revenue"),
    "current_ratio":("current_assets","current_liabilities"),
}
FORMULA_VERSION="cvm-basic-v1"

@dataclass(frozen=True)
class CalculatedIndicator:
    metric_code:str
    company_code:str
    period:str
    scope:str
    value:Decimal
    unit:str
    formula_version:str
    source_sha256:str
    account_codes:tuple[str,...]
    status:str="requires_source_review"

def calculate_indicators(lines:list[AccountingLine])->list[CalculatedIndicator]:
    if not lines:
        return []
    keys={(line.cvm_code,line.reference_date,line.scope,line.dataset_sha256,
           line.document_type,line.reporting_version) for line in lines}
    if len(keys)!=1:
        raise ValueError("mixed company, periods, scope, dataset or reporting versions")
    base=lines[0]
    if base.document_type!="dfp":
        raise ValueError("ITR cumulative/quarterly figures require separate normalization")
    mapped={}
    for line in lines:
        for label,(statement,account) in ACCOUNTS.items():
            if line.statement==statement and line.account_code==account:
                if label in mapped:
                    raise ValueError("duplicate account entry; explicit restatement selection required")
                if line.currency_scale not in SCALES:
                    raise ValueError("unknown currency scale")
                mapped[label]=(line.financial_value*SCALES[line.currency_scale],account)
    output=[]
    for name,(numerator,denominator) in RATIOS.items():
        if numerator not in mapped or denominator not in mapped:
            continue
        n,ncode=mapped[numerator];d,dcode=mapped[denominator]
        if d==0:
            continue
        value=n/d
        if not value.is_finite():
            continue
        output.append(CalculatedIndicator(metric_code=name,company_code=base.cvm_code,
            period=base.reference_date,scope=base.scope,value=value,unit="ratio",
            formula_version=FORMULA_VERSION,source_sha256=base.dataset_sha256,
            account_codes=(ncode,dcode)))
    return output
