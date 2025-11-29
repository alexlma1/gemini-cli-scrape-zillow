# Zillow scraper (LLM / no‑code via gemini‑cli)

This repo lets an LLM operate a Zillow scraping workflow end‑to‑end with minimal coding. It uses Playwright for navigation and Selectolax for parsing, and focuses on agent autonomy (gemini‑cli or similar) to append URLs, run scrapes, and collect results.

## Repo layout
- `zillowscrape/` – runnable scraper, data files, and agent docs (see its README for details).
- `demo/` – supporting assets (captured pages, CA certs) helpful for debugging and agent demos.

## Quick start (manual)
```bash
cd zillowscrape
python -m venv venv && source venv/bin/activate  # Win: venv\Scripts\activate
pip install playwright selectolax && python -m playwright install chromium
python zillow_scraper_playwright.py  # reads zillow_listing_urls.csv
```
Output: `zillowscrape/zillow_detailed_listings_playwright.json`.

## LLM / gemini‑cli usage
Examples of natural‑language tasks you can issue to your agent:
- "Open zillowscrape/README.md and summarize the steps to run the scraper."
- "Append these URLs to zillowscrape/zillow_listing_urls.csv and run the scraper."
- "If selectors break, propose minimal changes to zillow_scraper_playwright.py and re‑run."
- "Validate the JSON output and print a brief summary (count, average price, missing fields)."
- "Configure proxy settings if blocked, and explain how to trust the included CA certs."

Tip: grant the agent permission to execute shell commands in `zillowscrape/` and to edit `zillow_listing_urls.csv`.

## Compliance
Only scrape data you’re authorized to access; respect Zillow’s Terms, robots rules, and local laws.
