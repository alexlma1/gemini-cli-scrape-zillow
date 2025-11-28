
import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
from selectolax.parser import HTMLParser

def init_browser(p):
    browser = p.chromium.launch(headless=False) # Set False for debug
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        viewport={'width': 1920, 'height': 1080},
        # Mask automation signals
        java_script_enabled=True,
        bypass_csp=True
    )
    # Inject stealth scripts to override navigator.webdriver flags
    context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return context

def extract_media_assets(page):
    # 1. Trigger Modal
    try:
        page.click('button:has-text("See all")', timeout=5000) 
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
    except Exception as e:
        print(f"Could not extract media assets: {e}")
        return {"photos": [], "floor_plans": []}

def extract_amenities(page):
    # Click "Show More" if description is truncated
    try:
        page.locator('button:has-text("Show more")').click(timeout=2000)
    except:
        pass # Button might not exist
        
    data_tree = {}
    
    # Locate the main container for facts (Reference Screenshot 2)
    # Generic strategy: Find headers inside the amenities section
    try:
        sections = page.locator('div[class*="amenity-container"] h6').all()
        
        for header in sections:
            category_name = header.inner_text()
            # Get the sibling <ul> or container
            # Playwright locator strategy: locate the list strictly associated with this header
            items = header.locator("xpath=following-sibling::ul[1]//li").all_inner_texts()
            data_tree[category_name] = items
    except Exception as e:
        print(f"Could not extract amenities: {e}")
        
    return data_tree

def scrape_listing_details(page, url):
    page.goto(url, wait_until="domcontentloaded")
    
    # A good practice is to wait for a key element to be present
    page.wait_for_selector('h1', timeout=10000)

    html = HTMLParser(page.content())

    # Using selectolax for core attributes
    price_text = html.css_first('span[data-test-id="price"]')
    price = int("".join(filter(str.isdigit, price_text.text()))) if price_text else None

    sqft_text = html.css_first('span.sc-iMCRrC.ibNafl') # This selector is a guess, needs verification
    sqft = int("".join(filter(str.isdigit, sqft_text.text()))) if sqft_text else None

    address_street = html.css_first('h1[data-test-id="address-info-title-text"]')
    address_city_zip = html.css_first('p[data-test-id="address-info-secondary-text"]')
    
    listing_data = {
        "asset_id": url.split('/')[-2],
        "meta": {
            "scraped_at": datetime.utcnow().isoformat(),
            "listing_status": "Active" # Assuming active, can be improved
        },
        "core_attributes": {
            "price_monthly": price,
            "sqft": sqft,
            "address_blobs": {
                "street": address_street.text().strip() if address_street else None,
                "city": address_city_zip.text().split(',')[0].strip() if address_city_zip else None,
                "zip": address_city_zip.text().split(',')[1].strip().split(' ')[-1] if address_city_zip else None
            }
        },
        "media_index": extract_media_assets(page),
        "amenities_graph": extract_amenities(page),
        "agent_contact": { # Placeholder
            "name": None,
            "brokerage": None,
            "phone_encrypted": None,
            "phone_raw": None
        }
    }
    return listing_data

def main():
    with open('zillow_listing_urls.csv', 'r') as f:
        urls = [line.strip() for line in f.readlines()][:20]

    with sync_playwright() as p:
        context = init_browser(p)
        all_listings = []
        for url in urls:
            print(f"Scraping {url}")
            page = context.new_page()
            try:
                listing = scrape_listing_details(page, url)
                all_listings.append(listing)
            except Exception as e:
                print(f"Failed to scrape {url}: {e}")
            finally:
                page.close()
        
        context.close()

    with open('zillow_detailed_listings_playwright.json', 'w') as f:
        json.dump(all_listings, f, indent=2)
    
    print("Scraping complete. Data saved to zillow_detailed_listings_playwright.json")

if __name__ == '__main__':
    main()

