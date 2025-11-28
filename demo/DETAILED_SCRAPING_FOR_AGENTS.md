# Rental Asset Indexing Protocol (RAIP)

This document serves as the technical specification for the **Rental Asset Indexing Protocol (RAIP)**. It is intended for autonomous agents and engineers implementing high-fidelity extraction pipelines for Single Page Applications (SPAs) in the real estate domain (e.g., Zillow, Redfin, Compass).

-----

# AGENTS.md

**Version:** 2.1.0
**Context:** Dynamic DOM Extraction & Asset Indexing
**Target:** React/Next.js based Rental Marketplaces

-----

## 1\. Architectural Overview

The target listing pages rely heavily on Client-Side Rendering (CSR). Standard HTTP `GET` requests will yield incomplete DOM trees. The extraction agent must operate a headless browser instance to hydrate the state, execute JavaScript triggers, and capture lazy-loaded assets.

### The Stack

  * **Runtime:** Python 3.10+
  * **Driver:** `playwright` (Chromium context)
  * **DOM Parser:** `selectolax` (High-performance C-based parsing)
  * **OCR Layer:** `pytesseract` (For text-embedded-in-image data like floor plan dimensions or obfuscated phone numbers)

-----

## 2\. Data Schema Definition

The agent must normalize unstructured DOM elements into the following JSON schema. Do not flatten the data; preserve hierarchy.

```json
{
  "asset_id": "string (ZPID or internal UUID)",
  "meta": {
    "scraped_at": "ISO-8601",
    "listing_status": "Active | Pending | Off-Market"
  },
  "core_attributes": {
    "price_monthly": "integer",
    "sqft": "integer",
    "address_blobs": {
      "street": "string",
      "city": "string",
      "zip": "string"
    }
  },
  "media_index": {
    "high_res_photos": ["url_string"],
    "floor_plans": ["url_string"],
    "virtual_tours": ["url_string"]
  },
  "amenities_graph": {
    "unit_features": ["Valet Trash", "Quartz Countertops"],
    "building_services": ["Concierge", "Package Lockers"],
    "outdoor": ["Rooftop Deck", "BBQ Area"]
  },
  "agent_contact": {
    "name": "string",
    "brokerage": "string",
    "phone_encrypted": "boolean",
    "phone_raw": "string (post-interaction)"
  }
}
```

-----

## 3\. Execution Pipeline

### Phase A: Initialization & Fingerprint Evasion

Rental platforms utilize aggressive bot detection. The agent must initialize the browser context with specific masking parameters.

```python
from playwright.sync_api import sync_playwright

def init_browser(p):
    browser = p.chromium.launch(headless=True) # Set False for debug
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
        viewport={'width': 1920, 'height': 1080},
        # Mask automation signals
        java_script_enabled=True,
        bypass_csp=True
    )
    # Inject stealth scripts to override navigator.webdriver flags
    context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return context
```

### Phase B: Deep Media Extraction (The "Gallery" Interaction)

High-resolution images and floor plans are not present in the initial viewport. They are injected into the DOM only after a specific user interaction event.

**Logic:**

1.  Locate the trigger element (usually `button:has-text("See all photos")`).
2.  Fire `click` event.
3.  Wait for `div[role="dialog"]` (The Modal).
4.  Execute a **Scroll-and-Scrape** loop to trigger lazy-loading.

<!-- end list -->

```python
def extract_media_assets(page):
    # 1. Trigger Modal
    page.click('button:has-text("See all")') 
    page.wait_for_selector('div[role="dialog"]')
    
    # 2. Hydrate Lazy-Loaded Images
    # We must scroll the modal container, NOT the window
    modal = page.locator('div[role="dialog"]')
    last_height = 0
    
    for _ in range(10): # Max scroll attempts
        modal.evaluate("node => node.scrollTop += 1000")
        page.wait_for_timeout(500) # Allow network settle
        
    # 3. Extraction
    # Filter out low-res thumbnails often found in "films strips" at bottom
    image_elements = page.locator('div[role="dialog"] ul li img').all()
    
    assets = {
        "photos": [],
        "floor_plans": []
    }
    
    for img in image_elements:
        src = img.get_attribute('src')
        alt = img.get_attribute('alt').lower()
        
        # Heuristic: Detect Floor Plans via Alt Text or OCR (optional)
        if "floor" in alt or "plan" in alt:
            assets['floor_plans'].append(src)
        else:
            assets['photos'].append(src)
            
    return assets
```

### Phase C: Structural Text Parsing (Amenities)

Amenities are rarely flat lists. They are categorized (`<h2>` or `<h6>` headers followed by `<ul>` or `<dl>`).

**Extraction Logic:**
Use relative locators. Find the Header, then scrape the sibling List Items until the next Header.

```python
def extract_amenities(page):
    # Click "Show More" if description is truncated
    try:
        page.locator('button:has-text("Show more")').click(timeout=2000)
    except:
        pass # Button might not exist
        
    data_tree = {}
    
    # Locate the main container for facts (Reference Screenshot 2)
    # Generic strategy: Find headers inside the amenities section
    sections = page.locator('div[class*="amenity-container"] h6').all()
    
    for header in sections:
        category_name = header.inner_text()
        # Get the sibling <ul> or container
        # Playwright locator strategy: locate the list strictly associated with this header
        items = header.locator("xpath=following-sibling::ul[1]//li").all_inner_texts()
        data_tree[category_name] = items
        
    return data_tree
```

### Phase D: Agent & Contact Extraction

**Warning:** Contact info is often obfuscated or requires a "click-to-reveal" interaction (AJAX call).

1.  **Phone Numbers:** Look for `button:has-text("Call")` or hidden fields in the DOM named `broker_phone`.
2.  **Encryption:** If the phone number is an image (`<img src="phone_gen.php..."/>`), pass the image buffer to `pytesseract` for OCR extraction.
3.  **Tour Request Forms:** Ignore forms labeled "Request a tour" or "Apply". These are lead-gen forms for the platform, not direct contact methods for the agent.

-----

## 4\. Rate Limiting & Compliance

  * **Concurrency:** Maximum 2 concurrent threads per proxy IP.
  * **Retry Logic:** Implement exponential backoff (2s, 4s, 8s) on HTTP 403/429 errors.
  * **Robots.txt:** Agents must respect `Allow/Disallow` directives if scraping for public indexing.

## 5\. Heuristics for "Special" Features

*Referencing Screenshot 2 ("Valet Trash", "Quartz Countertops")*

To index "What's Special" or "High Value" tags:

  * Scan for CSS classes containing `badge`, `highlight`, or `feature-tag`.
  * Store these in a separate `highlight_tags` array in the schema. These are critical for the recommendation engine (e.g., "Show me apartments with Valet Trash").

-----

**End of Specification**