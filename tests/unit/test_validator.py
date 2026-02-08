from core.validators.corep_validator import CorepValidator


def test_validator_pass():

    schema = {
        "required": ["r010", "r020"],
        "derived": {"r030": "r010 + r020"},
        "currency": "GBP"
    }

    report = {
        "fields": {
            "r010": 100,
            "r020": 50,
            "r030": 150
        },
        "currency": "GBP"
    }

    validator = CorepValidator(schema)

    errors = validator.validate(report)

    assert errors == []


def test_validator_fail():

    schema = {
        "required": ["r010", "r020"],
        "derived": {"r030": "r010 + r020"},
        "currency": "GBP"
    }

    report = {
        "fields": {
            "r010": 100,
            "r020": 50,
            "r030": 140
        },
        "currency": "USD"
    }

    validator = CorepValidator(schema)

    errors = validator.validate(report)

    assert len(errors) > 0
