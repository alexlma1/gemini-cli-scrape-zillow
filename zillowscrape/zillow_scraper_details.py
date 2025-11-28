
import requests
from bs4 import BeautifulSoup
import time
import random
import json
import pandas as pd
from datetime import datetime

# Zillow URL for Seattle rentals
BASE_ZILLOW_URL = "https://www.zillow.com/seattle-wa/rentals/"

# Bright Data proxy details
PROXY_USERNAME = "brd-customer-hl_b746e33f-zone-mcp_unlocker"
PROXY_PASSWORD = "lwb03bz3qch0"
PROXY_HOST = "brd.superproxy.io"
PROXY_PORT = 33335 

proxies = {
    "http": f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}",
    "https": f"https://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}",
}

BRIGHTDATA_CERT_PATH = "brightdata_proxy_ca/New SSL certifcate - MUST BE USED WITH PORT 33335/BrightData SSL certificate (port 33335).crt"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def fetch_page(url):
    """Fetches a page using proxies and returns its content."""
    try:
        response = requests.get(url, proxies=proxies, headers=headers, timeout=20, verify=BRIGHTDATA_CERT_PATH)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def scrape_listing_details_from_url(url):
    """Scrapes detailed information from a single listing page by extracting __NEXT_DATA__."""
    print(f"Scraping details from: {url}")
    html = fetch_page(url)
    if not html:
        return None

    soup = BeautifulSoup(html, 'lxml')
    
    script_tag = soup.find('script', id='__NEXT_DATA__', type='application/json')
    if not script_tag:
        print("Could not find __NEXT_DATA__ script tag.")
        return None

    try:
        json_data = json.loads(script_tag.string)
        return json_data
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Error parsing JSON from __NEXT_DATA__: {e}")
        return None

def parse_listing_details(data, url):
    """Parses the __NEXT_DATA__ JSON and returns a dictionary conforming to the schema."""
    
    building_data = data.get('props', {}).get('pageProps', {}).get('componentProps', {}).get('initialReduxState', {}).get('gdp', {}).get('building', {})
    if not building_data:
        return None

    # Core Attributes
    address = building_data.get('address', {})
    core_attributes = {
        "price_monthly": None, # Will be populated from units
        "sqft": None, # Will be populated from units
        "address_blobs": {
            "street": address.get('streetAddress'),
            "city": address.get('city'),
            "zip": address.get('zipcode')
        }
    }

    # Media Index
    photos = []
    for photo in building_data.get('galleryPhotos', []):
        # Get the highest resolution jpeg image
        if photo.get('mixedSources', {}).get('jpeg'):
            photos.append(photo['mixedSources']['jpeg'][-1]['url'])

    media_index = {
        "high_res_photos": photos,
        "floor_plans": [], # Placeholder
        "virtual_tours": [] # Placeholder
    }

    # Amenities
    amenities_graph = {}
    structured_amenities = building_data.get('structuredAmenities', {})
    if structured_amenities:
        for section, value in structured_amenities.items():
            if isinstance(value, dict) and 'amenityGroups' in value:
                amenities_graph[value.get('title')] = {}
                for group in value.get('amenityGroups', []):
                    amenities_graph[value.get('title')][group.get('title')] = group.get('amenities')

    # Agent Contact
    contact_info = building_data.get('contactInfo', {})
    agent_contact = {
        "name": contact_info.get('agentFullName'),
        "brokerage": None, # Not available
        "phone_encrypted": None, # Not available
        "phone_raw": None # Not available
    }

    # Units - This is where price and sqft are
    units = building_data.get('units', [])
    if units:
        # For simplicity, we take the first unit's data
        core_attributes['price_monthly'] = units[0].get('price')
        core_attributes['sqft'] = units[0].get('sqft')


    listing = {
        "asset_id": url.split('/')[-2],
        "meta": {
            "scraped_at": datetime.utcnow().isoformat(),
            "listing_status": "Active"
        },
        "core_attributes": core_attributes,
        "media_index": media_index,
        "amenities_graph": amenities_graph,
        "agent_contact": agent_contact
    }

    return listing


def main():
    try:
        with open('zillow_listing_urls.csv', 'r') as f:
            urls_to_scrape = [line.strip() for line in f.readlines()][:20]
    except FileNotFoundError:
        print("Error: zillow_listing_urls.csv not found. Please run zillow_scraper.py first to generate the file.")
        return

    print(f"Found {len(urls_to_scrape)} URLs to scrape from zillow_listing_urls.csv")

    all_parsed_listings = []
    for url in urls_to_scrape:
        raw_data = scrape_listing_details_from_url(url)
        if raw_data:
            parsed_listing = parse_listing_details(raw_data, url)
            if parsed_listing:
                all_parsed_listings.append(parsed_listing)
        time.sleep(random.uniform(2, 5))

    if not all_parsed_listings:
        print("No listing details were parsed. Exiting.")
        return

    with open('zillow_detailed_listings_parsed.json', 'w') as f:
        json.dump(all_parsed_listings, f, indent=2)
    
    print("\nParsed data saved to zillow_detailed_listings_parsed.json")

if __name__ == "__main__":
    main()
