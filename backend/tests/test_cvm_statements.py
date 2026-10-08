from io import BytesIO
from zipfile import ZipFile
import pytest
from app.cvm_statements import parse_cvm_archive

HEADER="CD_CVM;DT_REFER;CD_CONTA;DS_CONTA;VL_CONTA;ORDEM_EXERC;ESCALA_MOEDA;VERSAO\n"

def archive(data:bytes,name="dfp_cia_aberta_DRE_con_2025.csv"):
    buffer=BytesIO()
    with ZipFile(buffer,"w") as file:
        file.writestr(name,data)
    return buffer.getvalue()

def test_cvm_parser_filters_company_and_preserves_scale():
    csv=(HEADER+"1234;2025-12-31;3.01;Receita;123,45;ÚLTIMO;MIL;2\n"+
         "5678;2025-12-31;3.01;Receita;999;ÚLTIMO;MIL;2\n"+
         "1234;2025-12-31;3.02;Despesa;10;PENÚLTIMO;MIL;2\n").encode()
    lines=parse_cvm_archive(archive(csv),cvm_code="1234",year=2025)
    assert len(lines)==1
    assert str(lines[0].financial_value)=="123.45"
    assert lines[0].currency_scale=="MIL"
    assert lines[0].scope=="consolidated"
    assert lines[0].reporting_version=="2"

def test_unknown_scale_rejected():
    csv=(HEADER+"1234;2025-12-31;3.01;Receita;100;ÚLTIMO;BILHÕES;1\n").encode()
    with pytest.raises(ValueError):
        parse_cvm_archive(archive(csv),cvm_code="1234",year=2025)

def test_path_traversal_zip_rejected():
    with pytest.raises(ValueError):
        parse_cvm_archive(archive(b"test","../untrusted.csv"),cvm_code="1234",year=2025)

def test_invalid_zip_rejected():
    with pytest.raises(ValueError):
        parse_cvm_archive(b"notzip",cvm_code="1234",year=2025)

def test_wrong_statement_year_skipped():
    assert parse_cvm_archive(archive(HEADER.encode(),"dfp_cia_aberta_DRE_con_2024.csv"),cvm_code="1234",year=2025)==[]
