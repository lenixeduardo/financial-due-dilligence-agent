"""Conservative allowlisted HTTP client for official-source ingestion.

Defense-in-depth: disable redirects and environment proxies, validate DNS resolution.
Network egress rules are still required to avoid DNS-rebinding/TOCTOU.
"""
from dataclasses import dataclass
from ipaddress import ip_address
import socket
from urllib.parse import urlparse
import httpx

ALLOWED_HOSTS = frozenset({"dados.cvm.gov.br", "www.gov.br", "www.bcb.gov.br"})
MAX_BYTES = 5 * 1024 * 1024

class UnsafeSource(ValueError):
    pass

def validate_url(url: str) -> str:
    parsed = urlparse(url)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.hostname.lower() not in ALLOWED_HOSTS
            or parsed.username or parsed.password or parsed.port not in (None, 443)
            or parsed.fragment):
        raise UnsafeSource("source URL not allowlisted")
    if parsed.hostname != parsed.netloc and parsed.netloc != f"{parsed.hostname}:443":
        raise UnsafeSource("unexpected authority")
    return url

def validate_resolution(hostname: str):
    try:
        records = socket.getaddrinfo(hostname, 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise UnsafeSource("DNS resolution unavailable") from exc
    if not records:
        raise UnsafeSource("no DNS records")
    for record in records:
        address = ip_address(record[4][0])
        if not address.is_global:
            raise UnsafeSource("non-public DNS address")

def download_official(url: str) -> bytes:
    """Preflight only; do not use without infrastructure egress restrictions."""
    validate_url(url)
    hostname = urlparse(url).hostname
    assert hostname is not None
    validate_resolution(hostname)
    with httpx.Client(follow_redirects=False, trust_env=False, timeout=10.0) as client:
        with client.stream("GET", url, headers={"Accept": "application/pdf, text/csv, application/json"}) as response:
            if response.status_code != 200:
                raise UnsafeSource(f"source HTTP status {response.status_code}")
            length = response.headers.get("Content-Length")
            if length and int(length) > MAX_BYTES:
                raise UnsafeSource("source too large")
            body = bytearray()
            for chunk in response.iter_bytes():
                body.extend(chunk)
                if len(body) > MAX_BYTES:
                    raise UnsafeSource("source too large")
            return bytes(body)
