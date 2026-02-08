class AuditLogger:
    """
    Builds audit trail for report fields.
    """

    @staticmethod
    def build(field: str, rule: str) -> dict:
        return {field: rule}
