# Zillow scraper (LLM / no‑code via gemini‑cli)

This is my first little project that convinced me to stop coding for fun. Here I am intending to demo a simple workflow using genai. This repo lets an LLM operate a Zillow scraping workflow end‑to‑end with minimal to zero code. It (genai loop) uses detailed instructions and that's it to collect data. The focus is on agent autonomy (gemini‑cli or similar) to complete a task. 

## Repo layout
- `zillowscrape/` – This contains the INFO.mds or (GEMINI.mds). The data it collected I did not upload nor the scripts it used.
- `demo/` – another version, the INFO.md files are slightly different this folder was meant to be clean for a demo.
  
# Quick start (manual)
```bash
cd zillowscrape
gemini --yolo
```
Enter the instructions below under usage.

Output a small database: `zillowscrape/zillow_detailed_listings_playwright.json` 

## LLM / gemini‑cli usage 
Say this to gemini-cli on yolo mode 
```
Example of a natural language instruction, that combined with the additional info allows the agent to complete the task.
Utilize the proxy framework to begin collecting listing pages starting at the url at the bottom of the GEMINI.md
Save this list of listing urls. Consult both the "listing indexing protocol" and the find the "next link" markdown files next. 
Using a headless browsing tool, extract all data from each listing on each listing url. 
This data includes, all typical rental characteristics, text descriptions,
contacts, location, as well as the url to each photo listed. Some listings have multiple units meaning the processs can be repeated more than once per listing.
All of this data is the final product.
```


## What did I get?
Several hundred MB of several thousand apartment listings are produced and saved in JSON format. 
The output data was all text. Links to each listing's pictures, and all of the relevant rental information you might need thoughtfully aggregated. Plus the run took approximately 30 minutes and cost <$10 of proxy (woops). 

## Compliance
Only scrape data you’re authorized to access; respect Zillow’s Terms, robots rules, and local laws.
