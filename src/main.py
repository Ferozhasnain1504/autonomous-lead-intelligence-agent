import argparse
import asyncio
import logging

from src.browser import BrowserEngine
from src.pipeline import EnrichmentPipeline
from src.output_writer import OutputWriter

def parse_args():
    parser = argparse.ArgumentParser(
        description="Autonomous Lead Intelligence Agent"
    )

    parser.add_argument(
        "domains",
        nargs="+",
        help="Company domains to enrich, e.g. postman.com supabase.com",
    )

    return parser.parse_args()

async def run(domains: list[str]):
    browser = BrowserEngine(headless=True)

    await browser.start()

    try:
        pipeline = EnrichmentPipeline(browser=browser)
        results = await pipeline.enrich_companies(domains)

        for domain, result in results.items():
            print("\n" + "=" * 60)
            print(f"COMPANY: {domain}")
            print("=" * 60)

            if result is None:
                print("Enrichment failed.")
                continue

            print(result.model_dump_json(indent=2))

        writer = OutputWriter()
        output_path = writer.write_json(results)

        print("\n" + "=" * 60)
        print("OUTPUT")
        print("=" * 60)
        print(f"Results written to: {output_path}")

    finally:
        await browser.close()


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    args = parse_args()
    asyncio.run(run(args.domains))


if __name__ == "__main__":
    main()