import logging
import os

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

logger = logging.getLogger(__name__)


class ExternalSearch:
    """Searches the public web for missing company/person information."""

    def __init__(self, client=None):
        self.client = client

        if self.client is None:
            api_key = os.getenv("TAVILY_API_KEY")

            if api_key:
                self.client = TavilyClient(api_key=api_key)

    async def find_linkedin_profile(
        self,
        person_name: str,
        company_name: str,
    ) -> str | None:
            """Find a likely LinkedIn profile for a person."""
            if self.client is None:
                logger.info("External search is not configured.")
                return None

            query = f"{person_name} {company_name} LinkedIn"

            try:
                response = self.client.search(
                    query=query,
                    include_domains=["linkedin.com"],
                    max_results=5,
                )

                results = response.get("results", [])

                for result in results:
                    url = result.get("url", "").strip()

                    if "linkedin.com/in/" in url:
                        logger.info(
                            "Found LinkedIn profile for %s: %s",
                            person_name,
                            url,
                        )
                        return url

                logger.info(
                    "No LinkedIn profile found for %s",
                    person_name,
                )
                return None

            except Exception as error:
                logger.warning(
                    "External search failed for %s: %s",
                    person_name,
                    error,
                )
                return None