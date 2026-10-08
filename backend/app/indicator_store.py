"""SQLite persistence of provenance-bearing calculated indicators."""
from .db import connection
from .cvm_indicators import CalculatedIndicator

SCHEMA="""
CREATE TABLE IF NOT EXISTS calculated_indicators (
 workspace_id TEXT NOT NULL REFERENCES workspaces(id),
 company_code TEXT NOT NULL,
 period TEXT NOT NULL,
 scope TEXT NOT NULL,
 metric_code TEXT NOT NULL,
 formula_version TEXT NOT NULL,
 dataset_sha256 TEXT NOT NULL,
 account_codes TEXT NOT NULL,
 value_decimal TEXT NOT NULL,
 status TEXT NOT NULL,
 PRIMARY KEY(workspace_id,company_code,period,scope,metric_code,formula_version,dataset_sha256)
);
CREATE INDEX IF NOT EXISTS indicator_scope_idx ON calculated_indicators(workspace_id,company_code,period);
"""

def persist_indicators(workspace_id:str,indicators:list[CalculatedIndicator])->int:
    if not workspace_id:
        raise ValueError("workspace required")
    with connection() as conn:
        conn.executescript(SCHEMA)
        total=0
        for item in indicators:
            cursor=conn.execute("""INSERT OR IGNORE INTO calculated_indicators(
              workspace_id,company_code,period,scope,metric_code,formula_version,
              dataset_sha256,account_codes,value_decimal,status)
              VALUES(?,?,?,?,?,?,?,?,?,?)""",
              (workspace_id,item.company_code,item.period,item.scope,item.metric_code,
               item.formula_version,item.source_sha256,",".join(item.account_codes),
               str(item.value),item.status))
            total+=cursor.rowcount
    return total

def get_indicators(workspace_id:str,company_code:str)->list[dict]:
    with connection() as conn:
        conn.executescript(SCHEMA)
        rows=conn.execute("""SELECT company_code,period,scope,metric_code,formula_version,
            dataset_sha256,account_codes,value_decimal,status FROM calculated_indicators
            WHERE workspace_id=? AND company_code=?
            ORDER BY period DESC,metric_code""",(workspace_id,company_code)).fetchall()
    return [dict(row) for row in rows]
