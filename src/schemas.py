from pydantic import BaseModel, Field, HttpUrl


class LeadershipPerson(BaseModel):
    name: str = Field(
        description="Full name of the person."
    )

    role: str = Field(
        description="Job title or role of the person."
    )

    linkedin_url: HttpUrl | None = Field(
        default=None,
        description="Public LinkedIn profile URL if discoverable.",
    )


class EvidenceItem(BaseModel):
    field: str = Field(
        description="The intelligence field supported by this evidence."
    )

    evidence: str = Field(
        description=(
            "A concise excerpt or factual statement supported "
            "by the supplied website content."
        )
    )


class CompanyIntelligence(BaseModel):
    company_name: str = Field(
        description="Official company name."
    )

    company_overview: str = Field(
        description=(
            "A concise two-sentence overview of what the company "
            "does and the value it provides."
        )
    )

    target_audience: str = Field(
        description=(
            "Description of the company's target audience, "
            "ideal customer profile, or ICP."
        )
    )

    public_emails: list[str] = Field(
        default_factory=list,
        description="Generic or publicly listed company email addresses.",
    )

    leadership: list[LeadershipPerson] = Field(
        default_factory=list,
        description=(
            "Key leadership or team members discovered from "
            "public company information."
        ),
    )

    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "Confidence in the overall extracted intelligence, "
            "between 0.0 and 1.0."
        ),
    )

    evidence: list[EvidenceItem] = Field(
        default_factory=list,
        description=(
            "Evidence supporting the extracted company intelligence."
        ),
    )