from app.local_agent import draft_interpretation
import pytest

def test_nonlocal_model_endpoint_rejected():
    with pytest.raises(ValueError):
        draft_interpretation(workspace_id="w",company_id="a",question="Revenue",
          model="demo",endpoint="http://example.org:11434")
