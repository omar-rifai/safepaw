import pytest
import json
from pathlib import Path

@pytest.fixture
def sample_params():
    with open(Path(__file__).parent/ "data" / "reference_params.json") as f:
        return json.load(f)

@pytest.fixture 
def sample_datamodel():
    from backend.core.data_models.input_models import SystemData
    
    with open(Path(__file__).parent/ "data" / "reference_datamodel.json") as f:
        data = json.load(f)
    
    return SystemData.model_validate(data)
    
