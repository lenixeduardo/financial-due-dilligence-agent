"""Bounded, explicit source ingestion; no arbitrary URL fetching or LLM assumptions."""
from hashlib import sha256
from io import BytesIO, StringIO
from pathlib import Path
import csv
from pypdf import PdfReader
from .db import connection
from .evidence import Evidence

MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_PAGES = 100
MAX_CHARS_PER_PAGE = 100_000
CHUNK_CHARS = 1200
CHUNK_OVERLAP = 150

def extract_pages(filename: str, content: bytes) -> list[str]:
    if not content or len(content) > MAX_FILE_BYTES:
        raise ValueError("document empty or exceeds 8 MB")
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        if not content.startswith(b"%PDF-"):
            raise ValueError("invalid PDF header")
        try:
            reader = PdfReader(BytesIO(content), strict=True)
            if reader.is_encrypted or len(reader.pages) > MAX_PAGES:
                raise ValueError("encrypted or oversized PDF not supported")
            pages = [(page.extract_text() or "").strip() for page in reader.pages]
        except ValueError:
            raise
        except Exception as error:
            raise ValueError("invalid or unsupported PDF") from error
    elif suffix in (".txt", ".csv"):
        try:
            decoded = content.decode("utf-8-sig")
        except UnicodeError as error:
            raise ValueError("UTF-8 required") from error
        if suffix == ".csv":
            # Validate parseability; keep original layout for grounded citations.
            list(csv.reader(StringIO(decoded)))
        pages = [decoded.strip()]
    else:
        raise ValueError("only PDF, TXT, CSV supported")
    if not pages or any(len(page) > MAX_CHARS_PER_PAGE for page in pages):
        raise ValueError("document exceeds parsing bounds")
    return pages

def chunk_text(text: str) -> list[str]:
    if not text.strip():
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + CHUNK_CHARS, len(text))
        part = text[start:end].strip()
        if part:
            chunks.append(part)
        if end >= len(text):
            break
        start = end - CHUNK_OVERLAP
    return chunks

def ingest_bytes(*, workspace_id: str, company_id: str, filename: str,
                 content: bytes, source_url: str, publisher: str, document_version: str) -> dict:
    if not workspace_id or not company_id or not publisher or not document_version:
        raise ValueError("required source metadata missing")
    pages = extract_pages(filename, content)
    digest = sha256(content).hexdigest()
    count = 0
    with connection() as conn:
        if not conn.execute("SELECT 1 FROM workspaces WHERE id=?", (workspace_id,)).fetchone():
            raise ValueError("workspace does not exist")
        for page_number, page_text in enumerate(pages, 1):
            if not page_text:
                continue
            page_id = sha256(f"{workspace_id}:{company_id}:{digest}:{page_number}".encode()).hexdigest()
            evidence = Evidence.create(id=page_id, workspace_id=workspace_id,
                company_id=company_id, source_url=source_url,
                publisher=publisher, document_version=document_version,
                page=page_number, text=page_text)
            row = conn.execute("SELECT content_sha256 FROM evidence WHERE id=?", (page_id,)).fetchone()
            if row:
                if row["content_sha256"] != evidence.sha256_hex:
                    raise ValueError("evidence identifier conflict")
                continue
            conn.execute("""INSERT INTO evidence
                (id,workspace_id,company_id,source_url,publisher,document_version,page,content_sha256,text_content)
                VALUES(?,?,?,?,?,?,?,?,?)""",
                (page_id,workspace_id,company_id,source_url,publisher,
                 document_version,page_number,evidence.sha256_hex,page_text))
            for index, part in enumerate(chunk_text(page_text)):
                conn.execute("""INSERT INTO evidence_chunks
                (id,evidence_id,workspace_id,company_id,page,chunk_order,body)
                VALUES(?,?,?,?,?,?,?)""",
                (f"{page_id}:{index}",page_id,workspace_id,company_id,page_number,index,part))
                count += 1
    return {"file_sha256":digest,"pages":len(pages),"new_chunks":count,"status":"indexed_unverified"}
