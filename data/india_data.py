from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib import request


USER_AGENT = "FinSight your.email@example.com"

# Add Indian companies here.
# These are official investor-relations pages where annual reports
# can be obtained.
INDIAN_COMPANIES = {
    "RELIANCE": {
        "name": "Reliance Industries",
        "investor_url": "https://www.ril.com/investors/financial-reporting",
    },
    "TCS": {
        "name": "Tata Consultancy Services",
        "investor_url": "https://www.tcs.com/investor-relations",
    },
    "INFY": {
        "name": "Infosys",
        "investor_url": "https://www.infosys.com/investors/",
    },
    "HDFCBANK": {
        "name": "HDFC Bank",
        "investor_url": "https://www.hdfcbank.com/personal/about-us/investor-relations",
    },
    "ICICIBANK": {
        "name": "ICICI Bank",
        "investor_url": "https://www.icicibank.com/about-us/investor-relations",
    },
}

OUTPUT_DIR = Path(__file__).resolve().parent / "india_downloads"


def get_bytes(url: str) -> bytes:
    req = request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml",
        },
    )

    with request.urlopen(req, timeout=60) as response:
        return response.read()


def download_company_page(ticker: str, company: dict) -> Path:
    company_dir = OUTPUT_DIR / ticker
    company_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading information for {company['name']}...")

    data = get_bytes(company["investor_url"])

    output_file = company_dir / "investor_relations.html"
    output_file.write_bytes(data)

    print(f"Saved: {output_file}")

    return output_file


def download_indian_data() -> dict:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest = {
        "source": "Indian company investor-relations pages",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "companies": [],
    }

    for ticker, company in INDIAN_COMPANIES.items():
        try:
            output_file = download_company_page(ticker, company)

            manifest["companies"].append(
                {
                    "ticker": ticker,
                    "name": company["name"],
                    "investor_url": company["investor_url"],
                    "local_path": str(
                        output_file.relative_to(OUTPUT_DIR)
                    ),
                }
            )

        except Exception as error:
            print(f"Failed to download {ticker}: {error}")

        time.sleep(1)

    manifest_path = OUTPUT_DIR / "manifest.json"

    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )

    return manifest


if __name__ == "__main__":
    result = download_indian_data()

    print(
        f"Downloaded information for "
        f"{len(result['companies'])} Indian company(s)"
    )

    print(f"Manifest: {OUTPUT_DIR / 'manifest.json'}")
