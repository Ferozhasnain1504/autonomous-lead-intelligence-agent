import json
from pathlib import Path

from src.schemas import CompanyIntelligence


class OutputWriter:
    """Writes enrichment results to structured JSON files."""

    def __init__(self, output_directory: str = "output"):
        self.output_directory = Path(output_directory)

    def write_json(
        self,
        results: dict[str, CompanyIntelligence | None],
        filename: str = "output.json",
    ) -> Path:
        self.output_directory.mkdir(parents=True, exist_ok=True)

        output_data = {}

        for domain, result in results.items():
            if result is None:
                output_data[domain] = {
                    "status": "failed",
                    "data": None,
                }
            else:
                output_data[domain] = {
                    "status": "success",
                    "data": result.model_dump(mode="json"),
                }

        output_path = self.output_directory / filename

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(
                output_data,
                file,
                indent=2,
                ensure_ascii=False,
            )

        return output_path