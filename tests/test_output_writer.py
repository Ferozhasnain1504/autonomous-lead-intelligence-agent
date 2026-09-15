import json

from src.output_writer import OutputWriter
from src.schemas import CompanyIntelligence


def create_sample_company():
    return CompanyIntelligence(
        company_name="Example Corp",
        company_overview=(
            "Example Corp builds software for developers. "
            "Its platform helps development teams work more efficiently."
        ),
        target_audience="Software developers",
        public_emails=["hello@example.com"],
        leadership=[],
        confidence_score=0.9,
    )


def test_write_json(tmp_path):
    writer = OutputWriter(output_directory=str(tmp_path))

    results = {
        "example.com": create_sample_company(),
    }

    output_path = writer.write_json(results)

    assert output_path.exists()

    with output_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    assert data["example.com"]["status"] == "success"
    assert data["example.com"]["data"]["company_name"] == "Example Corp"
    assert data["example.com"]["data"]["confidence_score"] == 0.9


def test_write_json_handles_failed_company(tmp_path):
    writer = OutputWriter(output_directory=str(tmp_path))

    results = {
        "good.com": create_sample_company(),
        "bad.com": None,
    }

    output_path = writer.write_json(results)

    with output_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    assert data["good.com"]["status"] == "success"
    assert data["bad.com"]["status"] == "failed"
    assert data["bad.com"]["data"] is None