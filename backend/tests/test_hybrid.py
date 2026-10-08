from math import inf
import pytest
from app.hybrid import validate_embedding, VECTOR_DIM

def test_embedding_shape():
    result=validate_embedding([0.0]*VECTOR_DIM)
    assert result.startswith("[") and result.endswith("]")

def test_wrong_dimension_rejected():
    with pytest.raises(ValueError):
        validate_embedding([0.1]*12)

def test_nonfinite_vector_rejected():
    with pytest.raises(ValueError):
        validate_embedding([0.0]*(VECTOR_DIM-1)+[inf])
