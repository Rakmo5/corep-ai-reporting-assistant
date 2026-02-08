import json
import os
from datetime import datetime


class ReportSaver:
    """
    Saves generated reports with metadata.
    """

    def __init__(self, output_dir: str = "outputs/reports"):

        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def save(self, report: dict, errors: list[str]) -> str:

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        status = "valid" if not errors else "invalid"

        filename = f"report_{timestamp}_{status}.json"

        path = os.path.join(self.output_dir, filename)

        payload = {
            "timestamp": timestamp,
            "status": status,
            "report": report,
            "validation_errors": errors
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        return path
