# Demo assets

This folder contains artifacts to help agents/LLMs plan, debug, and demonstrate the scraper.

- `cli.html`, `listing_page.html`, `page_*.html`: captured pages for selector inspection.
- `DETAILED_SCRAPING_FOR_AGENTS.md`, `How to find the "next" link.md`: guidance for pagination and extraction.
- `ca*.crt`, `brightdata_proxy_ca*`: CA materials for proxy/MITM setups when required.

Notes
- Do not install or trust CAs unless you understand the security implications and need proxy interception.
- These assets are optional for basic runs; see `../zillowscrape/README.md` for the primary workflow.
