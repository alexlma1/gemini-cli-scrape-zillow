import requests
from bs4 import BeautifulSoup
import time
import random
import json

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

def extract_listing_urls(html_content):
    """Extracts listing URLs and total pages from Zillow search results HTML content."""
    soup = BeautifulSoup(html_content, 'lxml')
    urls = set()
    
    script_tag = soup.find('script', id='__NEXT_DATA__', type='application/json')
    if not script_tag:
        print("Could not find __NEXT_DATA__ script tag.")
        return [], 0

    try:
        json_data = json.loads(script_tag.string)
        
        # Navigate to the list of results
        results = json_data.get('props', {}).get('pageProps', {}).get('searchPageState', {}).get('cat1', {}).get('searchResults', {}).get('listResults', [])
        total_pages = json_data.get('props', {}).get('pageProps', {}).get('searchPageState', {}).get('cat1', {}).get('searchList', {}).get('totalPages', 0)

        if not results:
            print("Could not find listResults in JSON data.")
            return [], 0

        for result in results:
            detail_url = result.get('detailUrl')
            if detail_url:
                if not detail_url.startswith('http'):
                    detail_url = "https://www.zillow.com" + detail_url
                urls.add(detail_url)

    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Error parsing JSON from __NEXT_DATA__: {e}")
        return [], 0
        
    return list(urls), total_pages

def main():
    all_urls = []
    MAX_LISTINGS_TO_SCRAPE = 20
    
    # Fetch the first page to get the total number of pages
    print(f"Fetching page 1: {BASE_ZILLOW_URL}")
    html = fetch_page(BASE_ZILLOW_URL)
    if not html:
        print("Failed to fetch the first page. Exiting.")
        return

    urls, total_pages = extract_listing_urls(html)
    if urls:
        print(f"Found {len(urls)} urls on page 1")
        all_urls.extend(urls)
    else:
        print(f"No URLs found on page 1. Saving page content for inspection.")
        with open(f"page_1_content.html", "w", encoding="utf-8") as f:
            f.write(html)

    if len(all_urls) >= MAX_LISTINGS_TO_SCRAPE:
        print(f"Collected {len(all_urls)} URLs, which is {MAX_LISTINGS_TO_SCRAPE} or more. Stopping.")
    elif total_pages > 1:
        for page_num in range(2, total_pages + 1):
            url = f"{BASE_ZILLOW_URL}{page_num}_p/"
            
            print(f"Fetching page {page_num}: {url}")
            html = fetch_page(url)
            
            if html:
                print(f"Extracting links from page {page_num}")
                urls, _ = extract_listing_urls(html)
                if urls:
                    print(f"Found {len(urls)} urls on page {page_num}")
                    all_urls.extend(urls)
                else:
                    print(f"No URLs found on page {page_num}. Saving page content for inspection.")
                    with open(f"page_{page_num}_content.html", "w", encoding="utf-8") as f:
                        f.write(html)
            
            if len(all_urls) >= MAX_LISTINGS_TO_SCRAPE:
                print(f"Collected {len(all_urls)} URLs, which is {MAX_LISTINGS_TO_SCRAPE} or more. Stopping.")
                break
            
            time.sleep(random.uniform(2, 5))

    print("\n--- All collected URLs ---")
    unique_urls = list(set(all_urls))
    
    # Limit to MAX_LISTINGS_TO_SCRAPE if more were collected
    unique_urls = unique_urls[:MAX_LISTINGS_TO_SCRAPE]

    for url in unique_urls:
        print(url)
    
    print(f"\nTotal unique URLs collected: {len(unique_urls)}")

    # Save the URLs to a CSV file
    with open("zillow_listing_urls.csv", "w") as f:
        for url in unique_urls:
            f.write(url + "\n")
    print("Saved collected URLs to zillow_listing_urls.csv")

if __name__ == "__main__":
    main()
