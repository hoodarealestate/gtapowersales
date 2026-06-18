import os
import requests
from bs4 import BeautifulSoup
import json
import re

def scrape_properties():
    url = os.environ.get('TARGET_URL')
    if not url:
        print("No URL provided!")
        return
        
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        print(f"Scraping main page: {url}")
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Failed to fetch page. Status: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        properties = []
        
        # Try different possible selectors for property cards
        # The website might use different class names
        possible_selectors = [
            'div.listing-item',
            'div.property-card',
            'div.listing-card',
            'div.property-item',
            'tr.listing-row',
            'div[class*="listing"]',
            'div[class*="property"]'
        ]
        
        listings = []
        for selector in possible_selectors:
            listings = soup.select(selector)
            if listings:
                print(f"Found {len(listings)} listings with selector: {selector}")
                break
        
        if not listings:
            print("No listings found with common selectors. Trying to find all divs...")
            # Fallback: find all divs and look for ones with price/address
            all_divs = soup.find_all('div')
            for div in all_divs:
                text = div.get_text()
                if '$' in text and ('Bed' in text or 'Bath' in text):
                    listings.append(div)
            
            print(f"Found {len(listings)} potential listings")
        
        for listing in listings:
            try:
                # Try to extract data with various selectors
                address = "Address Not Available"
                price = "Price Not Available"
                beds = "0"
                baths = "0"
                dom = "0"
                mls = ""
                
                # Look for address
                for selector in ['h2', 'h3', '.address', '[class*="address"]', '[class*="addr"]']:
                    addr_elem = listing.select_one(selector)
                    if addr_elem:
                        addr_text = addr_elem.get_text(strip=True)
                        if len(addr_text) > 5 and ',' in addr_text:
                            address = addr_text
                            break
                
                # Look for price
                for selector in ['.price', '[class*="price"]', 'span']:
                    price_elem = listing.select_one(selector)
                    if price_elem:
                        price_text = price_elem.get_text(strip=True)
                        if '$' in price_text:
                            price = price_text
                            break
                
                # Look for beds/baths in text
                text = listing.get_text()
                bed_match = re.search(r'(\d+)\s*Bed', text, re.IGNORECASE)
                bath_match = re.search(r'(\d+)\s*Bath', text, re.IGNORECASE)
                dom_match = re.search(r'(\d+)\s*DOM', text, re.IGNORECASE)
                mls_match = re.search(r'[A-Z]\d{8}', text)
                
                if bed_match: beds = bed_match.group(1)
                if bath_match: baths = bath_match.group(1)
                if dom_match: dom = dom_match.group(1)
                if mls_match: mls = mls_match.group(0)
                
                if address != "Address Not Available" or price != "Price Not Available":
                    properties.append({
                        'id': mls.lower() if mls else str(len(properties)),
                        'mls': mls,
                        'address': address,
                        'price': price,
                        'beds': beds,
                        'baths': baths,
                        'dom': dom,
                        'type': 'Residential',
                        'description': '',
                        'images': [],
                        'status': 'Active'
                    })
            except Exception as e:
                print(f"Error parsing listing: {e}")
                continue
        
        # Save to JSON
        with open('properties.json', 'w') as f:
            json.dump(properties, f, indent=2)
        
        print(f"✅ Successfully scraped {len(properties)} properties with data!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    scrape_properties()
