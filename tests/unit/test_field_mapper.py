import pytest
from core.tools.field_mapper import FieldMapper


def test_valid_mapping():

    assert FieldMapper.get_field("tier1") == "r010"
    assert FieldMapper.get_field("tier2") == "r020"
    assert FieldMapper.get_field("total") == "r030"


def test_invalid_mapping():

    with pytest.raises(ValueError):
        FieldMapper.get_field("unknown")
