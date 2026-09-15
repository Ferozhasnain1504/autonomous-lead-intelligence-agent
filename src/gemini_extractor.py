from dotenv import load_dotenv
from google import genai

from src.schemas import CompanyIntelligence


load_dotenv()


class GeminiExtractor:
    """Extracts structured company intelligence using Gemini."""

    def __init__(
        self,
        client=None,
        model: str = "gemini-3.5-flash",
    ):
        self.model = model
        self.client = client or genai.Client()

    async def extract(
        self,
        company_text: str,
    ) -> CompanyIntelligence:
        """
        Extract structured company intelligence from cleaned
        website content.
        """

        if not company_text.strip():
            raise ValueError("Company text cannot be empty.")

        prompt = self._build_prompt(company_text)

        interaction = self.client.interactions.create(
            model=self.model,
            input=prompt,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": CompanyIntelligence.model_json_schema(),
            },
        )

        if not interaction.output_text:
            raise ValueError("Gemini returned an empty response.")

        return CompanyIntelligence.model_validate_json(
            interaction.output_text
        )

    def _build_prompt(self, company_text: str) -> str:
        """Build the extraction prompt."""

        return f"""
You are an AI company intelligence extraction agent.

Your task is to extract structured information about a company
from the public website content provided below.

IMPORTANT RULES:

1. Use ONLY the information provided in the website content.
2. Do NOT invent or guess information.
3. If information is not available, use an empty list where
   appropriate.
4. Only include publicly listed generic/company email addresses.
5. Only include leadership or key team members that are
   explicitly supported by the provided content.
6. Only include LinkedIn URLs if they are explicitly present.
7. The company overview must be exactly two concise sentences.
8. The target audience should describe the company's customers,
   users, or ideal customer profile based on the evidence.
9. confidence_score must be between 0.0 and 1.0.
10. Give a higher confidence score when the website evidence
    strongly supports the extracted information.
11. Do not use outside knowledge.

Return ONLY information supported by the supplied website content.

WEBSITE CONTENT:
----------------
{company_text}
----------------
"""