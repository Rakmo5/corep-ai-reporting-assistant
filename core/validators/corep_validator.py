class CorepValidator:
    """
    Validates COREP report output.
    """

    def __init__(self, schema: dict):

        self.schema = schema

    def validate(self, report: dict) -> list[str]:
        """
        Validate generated report.
        Returns list of errors.
        """

        errors = []

        fields = report.get("fields", {})

        # 1️⃣ Check required fields
        for field in self.schema.get("required", []):

            if field not in fields:
                errors.append(f"Missing required field: {field}")

        # 2️⃣ Check derived fields
        derived = self.schema.get("derived", {})

        for field, formula in derived.items():

            try:
                # Example: r030 = r010 + r020
                if "+" in formula:

                    parts = formula.split("+")

                    a = fields.get(parts[0].strip())
                    b = fields.get(parts[1].strip())

                    if a is None or b is None:
                        errors.append(f"Cannot compute {field}")

                    else:
                        expected = a + b

                        if fields.get(field) != expected:
                            errors.append(
                                f"{field} mismatch: expected {expected}, got {fields.get(field)}"
                            )

            except Exception:
                errors.append(f"Error validating derived field: {field}")

        # 3️⃣ Check currency
        expected_currency = self.schema.get("currency")

        if expected_currency:

            if report.get("currency") != expected_currency:
                errors.append(
                    f"Invalid currency: expected {expected_currency}, got {report.get('currency')}"
                )

        return errors
