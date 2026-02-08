class FieldMapper:
    """
    Maps business concepts to COREP field codes.
    """

    FIELD_MAP = {
        "cet1": "r010",
        "at1": "r015",
        "tier1": "r020",
        "tier2": "r025",
        "total": "r030",
        "rwa": "r050",
        "cet1_ratio": "r060",
        "tier1_ratio": "r070",
        "total_ratio": "r080"
    }

    @classmethod
    def get_field(cls, name: str):

        if name not in cls.FIELD_MAP:
            raise ValueError(f"Unknown field: {name}")

        return cls.FIELD_MAP[name]
