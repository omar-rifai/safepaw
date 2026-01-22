from backend.core.mappers.input_mappers import convert_dm_to_json
from tests.conftests import sample_params, sample_datamodel

from pathlib import Path

def test_convert_dm_to_json(sample_datamodel, sample_params):

    system_params, _ = convert_dm_to_json(sample_datamodel)
    assert system_params ==  sample_params