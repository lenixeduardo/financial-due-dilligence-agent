import pytest
from app.sources import validate_url, UnsafeSource, validate_resolution
from unittest.mock import patch
import socket

@pytest.mark.parametrize("url",[
    "http://dados.cvm.gov.br/data",
    "https://127.0.0.1/",
    "https://metadata.google.internal/",
    "https://dados.cvm.gov.br.evil.test/",
    "https://dados.cvm.gov.br@evil.test/",
    "https://evil.test@dados.cvm.gov.br/",
    "https://dados.cvm.gov.br:444/",
    "https://www.bcb.gov.br/path#frag",
])
def test_block_unsafe_url(url):
    with pytest.raises(UnsafeSource):
        validate_url(url)

def test_allow_official_source():
    assert validate_url("https://dados.cvm.gov.br/dados/")=="https://dados.cvm.gov.br/dados/"

def test_private_resolution_rejected():
    with patch("socket.getaddrinfo",return_value=[(socket.AF_INET,socket.SOCK_STREAM,6,"",("10.1.1.1",443))]):
        with pytest.raises(UnsafeSource):
            validate_resolution("dados.cvm.gov.br")
