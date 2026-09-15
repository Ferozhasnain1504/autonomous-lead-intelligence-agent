# Autonomous Lead Intelligence Agent

An AI-powered company intelligence pipeline that crawls public company websites, discovers relevant pages, cleans webpage content, extracts structured business intelligence using Gemini, validates the result with Pydantic, and optionally searches the public web for missing LinkedIn profiles.

The project is designed as a resilient asynchronous pipeline where a failure on one company does not stop enrichment for the remaining companies.

---

## Features

- Automated browser-based webpage retrieval using Playwright
- Relevant page discovery for pages such as:
  - About
  - Company
  - Team
  - Contact
  - Pricing
- HTML/DOM cleaning using BeautifulSoup
- Removal of scripts, styles, SVGs, navigation noise, and other unnecessary content
- Structured company intelligence extraction using Gemini
- Pydantic schema validation
- Company overview generation
- Target audience / ICP extraction
- Public email extraction
- Leadership and team member extraction
- Public LinkedIn URL extraction when available
- Evidence tracking for extracted intelligence
- Confidence scoring from 0.0 to 1.0
- External LinkedIn search fallback using Tavily
- Graceful handling of:
  - 404 pages
  - Invalid URLs
  - Timeouts
  - Browser failures
  - Missing content
  - Gemini/API failures
  - Missing LinkedIn profiles
- Multiple-company processing
- Structured JSON output
- Token usage and estimated API cost tracking
- Automated test suite

---

## Architecture

```text
Company Domains
       |
       v
+-------------------+
| Playwright Browser|
+-------------------+
       |
       v
Homepage Retrieval
       |
       v
Relevant Page Discovery
       |
       +---- /about
       +---- /company
       +---- /team
       +---- /contact
       +---- /pricing
       |
       v
+----------------------+
| Content Cleaning     |
| BeautifulSoup / DOM  |
+----------------------+
       |
       v
Clean Company Text
       |
       v
+----------------------+
| Gemini Extraction    |
| Structured Output    |
+----------------------+
       |
       v
+----------------------+
| Pydantic Validation  |
+----------------------+
       |
       v
Evidence + Confidence
       |
       v
Missing LinkedIn URLs?
       |
      Yes
       |
       v
+----------------------+
| Tavily Web Search    |
+----------------------+
       |
       v
Enriched Company Data
       |
       v
+----------------------+
| JSON Output          |
+----------------------+
```

## Tech Stack
```
| Technology     | Purpose                                  |
| -------------- | ---------------------------------------- |
| Python         | Core application                         |
| Playwright     | Browser automation and webpage retrieval |
| BeautifulSoup  | HTML parsing and content cleaning        |
| lxml           | HTML parsing support                     |
| Pydantic       | Structured data validation               |
| Gemini API     | Company intelligence extraction          |
| Tavily         | External public-web search fallback      |
| python-dotenv  | Environment variable management          |
| asyncio        | Asynchronous pipeline execution          |
| pytest         | Automated testing                        |
| pytest-asyncio | Async test support                       |

```
## Project Structure
```
autonomous-lead-intelligence-agent/
|
├── src/
│   ├── __init__.py
│   ├── browser.py
│   ├── content_cleaner.py
│   ├── cost_tracker.py
│   ├── external_search.py
│   ├── gemini_extractor.py
│   ├── main.py
│   ├── output_writer.py
│   ├── page_discovery.py
│   ├── pipeline.py
│   ├── safe_runner.py
│   └── schemas.py
|
├── tests/
│   ├── test_browser.py
│   ├── test_content_cleaner.py
│   ├── test_cost_tracker.py
│   ├── test_external_search.py
│   ├── test_gemini_extractor.py
│   ├── test_output_writer.py
│   ├── test_page_discovery.py
│   ├── test_pipeline.py
│   ├── test_safe_runner.py
│   └── test_schemas.py
|
├── output/
│   └── output.json
|
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Installation
### 1. Clone the repository
```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd autonomous-lead-intelligence-agent
```
### 2. Create a virtual environment
- Windows: 
```bash
python -m venv .venv
```
- Activate it:
```bash
.venv\Scripts\activate
```
- macOS/Linux:
```bash
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Playwright browsers
```bash
playwright install
```

## Environment Variables
Create a `.env` file in the project root:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```
`.env` should never be committed to Git.
Tavily is optional. If it is not configured, the core company enrichment pipeline can still run and missing LinkedIn profiles are simply left unavailable.

## Running the Agent
The command-line interface accepts company domains.
Example:
```bash
python -m src.main postman.com
```
Multiple companies can be processed in one run:
```bash
python -m src.main postman.com supabase.com vapi.ai
```
The pipeline processes each company independently and records failures without stopping the entire run.

## Example Target Companies
The assignment test targets include:
```
postman.com
supabase.com
vapi.ai
```
Run all three:
```bash
python -m src.main postman.com supabase.com vapi.ai
```

## Output 
The pipeline generates structured JSON containing the enrichment result for each company.

Example structure:
```bash
{
  "postman.com": {
    "status": "success",
    "data": {
      "company_name": "Postman, Inc.",
      "company_overview": "...",
      "target_audience": "...",
      "public_emails": [],
      "leadership": [],
      "confidence_score": 0.95,
      "evidence": []
    }
  }
}
```
Each company result contains:

- company_name
- company_overview
- target_audience
- public_emails
- leadership
- confidence_score
- evidence

## Structured Extraction 
The Gemini extraction layer uses a Pydantic schema to constrain and validate the model output.

The system extracts:

#### Company Overview
A concise two-sentence description of what the company does and the value it provides.

#### Target Audience
The company's target users, customers, or ideal customer profile.

#### Public Emails
Generic or publicly listed company email addresses discovered from supplied website content.

#### Leadership
Publicly discoverable leadership/team information:
```bash
{
  "name": "Person Name",
  "role": "CEO",
  "linkedin_url": null
}
```

#### Confidence Score

A value between:
```text
0.0
```

and
```text
1.0
```
The score is based on the strength and completeness of the available website evidence.

#### Evidence

The system records concise supporting evidence for important extracted fields rather than returning unsupported claims.

## Resilience
A core design goal is to prevent one failed company from terminating the complete enrichment run.

Examples of handled failures include:

- Invalid URLs
- HTTP 404 responses
- Browser navigation failures
- Timeouts
- Missing webpage content
- Failed page discovery
- Invalid Gemini responses
- Gemini/API failures
- Missing LinkedIn profiles
- External search failures

Failures are handled through safe execution and company-level isolation.

## External LinkedIn Search
When a leadership person is discovered without a LinkedIn URL, the pipeline can optionally use Tavily to search the public web.

The search is restricted to LinkedIn results and looks for public profile URLs matching:
```text
linkedin.com/in/
```
If no suitable profile is found, the field remains null.

This fallback is intentionally best-effort rather than fabricating a profile URL

## Cost Tracking 
The project includes a provider-independent usage tracker for:

-Input tokens
- Output tokens
- Total tokens
- Number of API requests
- Estimated API cost

The tracker can be supplied with provider-specific input and output pricing.

## Testing

Run the complete test suite:
```
pytest -q
```
The current test suite covers:

- Browser retrieval
- 404 handling
- Invalid URL handling
- Page discovery
- Content cleaning
- Schema validation
- Confidence score validation
- Evidence validation
- Gemini extraction
- Empty extraction input
- Malformed Gemini responses
- Gemini/API failures
- Pipeline behavior
- Multiple-company processing
- LinkedIn enrichment
- Existing LinkedIn preservation
- External search behavior
- Cost tracking
- Safe execution
- JSON output

Current status:
```
36 passed
```
Tests use mocked/fake clients where appropriate, so the test suite does not depend on live Gemini or Tavily API responses.

## Design Decisions
### Why Playwright?

Some modern websites rely heavily on JavaScript. A browser-based retrieval layer allows the system to work with dynamically rendered content rather than depending only on basic HTTP requests.

### Why clean webpage content?

Raw HTML contains scripts, styles, SVGs, navigation elements, and other content that is not useful for company intelligence extraction.

Cleaning the content reduces noise before sending it to the LLM.

### Why Pydantic?

Pydantic provides explicit schemas and runtime validation for the structured intelligence returned by the model.

### Why Gemini?

Gemini is used as the LLM provider for structured company intelligence extraction.

### Why separate external search?

Website crawling and external discovery are separate responsibilities.

The crawler provides first-party company information, while the external search layer is used only as a fallback for missing public LinkedIn profiles.

## Limitations
- Public website information can be incomplete or outdated.
- Some websites may block automated browsers.
- Leadership information may not be available on a company's public website.
- LinkedIn profile discovery is best-effort.
- Confidence scores are heuristic estimates based on available evidence.
- API costs depend on model usage and provider pricing.
- The system does not attempt to access private or authenticated information.

## Security
- API keys are loaded through environment variables.
- ```.env``` is excluded from version control.
- Only publicly available website information is processed.
- The system does not attempt to bypass authentication or access private information.

## Future Improvements

Potential extensions include:

- Better relevance ranking for discovered pages
- More advanced entity resolution
- Search result confidence validation
- Persistent lead storage
- CSV export
- Database integration
- More detailed token/cost reporting
- Additional search providers
- Retry policies with exponential backoff
- Concurrent processing with configurable limits
- Lead scoring based on extracted ICP signals
## Author
Feroz Hasnain
