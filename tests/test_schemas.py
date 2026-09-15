import pytest
from pydantic import ValidationError

from src.schemas import CompanyIntelligence, EvidenceItem, LeadershipPerson


def test_leadership_person():
    person = LeadershipPerson(
        name="Jane Doe",
        role="CEO",
        linkedin_url="https://www.linkedin.com/in/janedoe",
    )

    assert person.name == "Jane Doe"
    assert person.role == "CEO"
    assert str(person.linkedin_url) == (
        "https://www.linkedin.com/in/janedoe"
    )


def test_company_intelligence():
    company = CompanyIntelligence(
        company_name="Example Corp",
        company_overview=(
            "Example Corp builds software for developers. "
            "Its platform helps teams collaborate efficiently."
        ),
        target_audience="Software development teams",
        public_emails=["info@example.com"],
        leadership=[
            LeadershipPerson(
                name="Jane Doe",
                role="CEO",
            )
        ],
        confidence_score=0.9,
        evidence=[
            EvidenceItem(
                field="company_overview",
                evidence="Example Corp builds software for developers.",
            )
        ],
    )

    assert company.company_name == "Example Corp"
    assert len(company.public_emails) == 1
    assert len(company.leadership) == 1
    assert company.confidence_score == 0.9
    assert company.evidence[0].field == "company_overview"
    assert company.evidence[0].evidence == (
        "Example Corp builds software for developers."
    )


def test_empty_optional_lists_are_allowed():
    company = CompanyIntelligence(
        company_name="Example Corp",
        company_overview="A software company. It builds developer tools.",
        target_audience="Developers",
        confidence_score=0.5,
    )

    assert company.public_emails == []
    assert company.leadership == []
    assert company.evidence == []


def test_confidence_score_cannot_exceed_one():
    with pytest.raises(ValidationError):
        CompanyIntelligence(
            company_name="Example Corp",
            company_overview="A software company. It builds tools.",
            target_audience="Developers",
            confidence_score=1.5,
        )


def test_confidence_score_cannot_be_negative():
    with pytest.raises(ValidationError):
        CompanyIntelligence(
            company_name="Example Corp",
            company_overview="A software company. It builds tools.",
            target_audience="Developers",
            confidence_score=-0.1,
        )

def test_evidence_item():
    evidence = EvidenceItem(
        field="company_overview",
        evidence="Example Corp builds software for developers.",
    )

    assert evidence.field == "company_overview"
    assert evidence.evidence == (
        "Example Corp builds software for developers."
    )