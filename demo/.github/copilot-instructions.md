# Copilot instructions for `zillowscrape`

## Snapshot
- Repo currently has two files: `settings` (text config) and `zillowscrape` (stub containing only `gemini`).
- There is no package manifest, dependencies, or tests; treat this repository as a placeholder awaiting upstream scraper code.
- The trailing `MLun` line in `settings` looks like external bookkeeping—leave it untouched until the maintainer clarifies its purpose.

## Proxy credentials
- `settings` → `BrowserProxy` lists `puppeteerplaywright` and `selenium` proxy endpoints that already include credentials.
- Secrets must live in environment variables; use the `.env` placeholders `BROWSER_PROXY_PUPPETEERPLAYWRIGHT` and `BROWSER_PROXY_SELENIUM` and fetch real values out of band.
- When adding code, read proxy URLs from env first and fall back to `settings` only if stakeholders confirm that fallback is required.

## Getting real scraper code
- Before writing scrapers, ask the maintainers where the canonical source lives (private repo, packaged artifact, etc.).
- Document any bootstrap step (download script, dependency install, credential retrieval) here once discovered so others can reproduce it quickly.
- Avoid committing scaffolding that assumes a specific language or framework until the upstream tech stack is confirmed.

## Developer workflow placeholders
- No build or test commands exist yet; once upstream code is synced, record the exact setup/run workflow in this section.
- Keep interim changes reversible so the authentic project can drop in without painful merges.

## Collaboration
- Flag uncertainties (missing modules, proxy rotations, Zillow flows) in PR descriptions for quick maintainer triage.
- Append newly uncovered conventions to this file so future agents can skip the discovery phase.
