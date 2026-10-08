"""Safe offline parsing of CVM DFP/ITR annual ZIP datasets, with explicit provenance.

No financial ratios are inferred here. Statements preserve supplied accounting scale.
"""
import csv
import hashlib
import io
import re
import zipfile
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

MAX_ARCHIVE_BYTES=32*1024*1024
MAX_MEMBERS=100
MAX_MEMBER_BYTES=45*1024*1024
MAX_TOTAL_BYTES=120*1024*1024
MAX_ROWS=300_000
FILE_RE=re.compile(r"^(dfp|itr)_cia_aberta_(BPA|BPP|DRE|DFC_MI|DFC_MD)_(con|ind)_(20\d\d)\.csv$",re.I)
REQUIRED={"CD_CVM","DT_REFER","CD_CONTA","DS_CONTA","VL_CONTA","ORDEM_EXERC"}
SCALES={"UNIDADE":Decimal("1"),"MIL":Decimal("1000")}

@dataclass(frozen=True)
class AccountingLine:
    source_file: str
    dataset_sha256: str
    document_type: str
    statement: str
    scope: str
    archive_year: int
    cvm_code: str
    reference_date: str
    account_code: str
    account_description: str
    financial_value: Decimal
    currency_scale: str
    presentation_order: str
    reporting_version: str

def parse_cvm_archive(raw: bytes, *, cvm_code: str, year: int, document_type: str="dfp") -> list[AccountingLine]:
    if document_type not in ("dfp","itr") or not re.fullmatch(r"\d{1,8}",cvm_code) or not 2010<=year<=2100:
        raise ValueError("invalid CVM selection")
    if not raw or len(raw)>MAX_ARCHIVE_BYTES:
        raise ValueError("archive exceeds safety limit")
    result=[]
    digest=hashlib.sha256(raw).hexdigest()
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            members=archive.infolist()
            if len(members)>MAX_MEMBERS or sum(i.file_size for i in members)>MAX_TOTAL_BYTES:
                raise ValueError("archive expansion limit exceeded")
            for info in members:
                if info.is_dir():
                    continue
                # Ignore unrelated resources; never write ZIP members to the filesystem.
                if "/" in info.filename or "\\" in info.filename:
                    raise ValueError("nested ZIP member paths forbidden")
                if info.flag_bits & 1 or info.file_size>MAX_MEMBER_BYTES:
                    raise ValueError("encrypted or oversized member")
                match=FILE_RE.fullmatch(info.filename)
                if not match:
                    continue
                kind,statement,scope,archive_year=match.groups()
                if kind.lower()!=document_type or int(archive_year)!=year:
                    continue
                with archive.open(info) as stream:
                    content=stream.read(MAX_MEMBER_BYTES+1)
                if len(content)>MAX_MEMBER_BYTES:
                    raise ValueError("member size exceeded")
                try:
                    decoded=content.decode("utf-8-sig")
                except UnicodeDecodeError:
                    decoded=content.decode("latin-1")
                reader=csv.DictReader(io.StringIO(decoded),delimiter=";")
                if not reader.fieldnames or not REQUIRED.issubset(set(reader.fieldnames)):
                    raise ValueError("missing required CVM CSV columns")
                for row_number,row in enumerate(reader,1):
                    if row_number>MAX_ROWS:
                        raise ValueError("too many statement rows")
                    if (row.get("CD_CVM") or "").strip()!=cvm_code:
                        continue
                    if (row.get("ORDEM_EXERC") or "").strip()!="ÚLTIMO":
                        continue
                    ref=(row.get("DT_REFER") or "").strip()
                    if not ref.startswith(str(year)+"-"):
                        continue
                    scale=(row.get("ESCALA_MOEDA") or "").strip().upper()
                    # Keep original amount rather than silently multiplying scales.
                    if scale not in SCALES:
                        raise ValueError("unknown accounting scale")
                    amount=(row.get("VL_CONTA") or "").strip().replace(",",".")
                    try:
                        value=Decimal(amount)
                    except InvalidOperation as error:
                        raise ValueError("non-numeric accounting value") from error
                    if not value.is_finite():
                        raise ValueError("non-finite accounting value")
                    result.append(AccountingLine(
                        source_file=info.filename,dataset_sha256=digest,
                        document_type=document_type,statement=statement.upper(),
                        scope="consolidated" if scope.lower()=="con" else "standalone",
                        archive_year=year,cvm_code=cvm_code,reference_date=ref,
                        account_code=(row.get("CD_CONTA") or "").strip(),
                        account_description=(row.get("DS_CONTA") or "").strip(),
                        financial_value=value,currency_scale=scale,
                        presentation_order="ÚLTIMO",
                        reporting_version=(row.get("VERSAO") or "").strip()))
    except (zipfile.BadZipFile,EOFError) as error:
        raise ValueError("invalid ZIP archive") from error
    return result
