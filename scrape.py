import os
import requests
from bs4 import BeautifulSoup
import json
import re
import time
import html

def scrape_properties():
    url = os.environ.get('TARGET_URL')
    if not url:
        print("No URL provided!")
        return
        
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        # Extract MLS numbers from URL
        mls_numbers = re.findall(r'[A-Z]\d{8}', url.upper())
        mls_numbers = list(dict.fromkeys(mls_numbers))
        print(f"Found {len(mls_numbers)} MLS numbers.")
        
        properties = []
        
        for mls in mls_numbers:
            detail_url = f"https://app.realmmlp.ca/listings/TREB-{mls}"
            print(f"Scraping {mls}...")
            
            response = requests.get(detail_url, headers=headers)
            if response.status_code != 200:
                print(f"Failed to fetch {mls}")
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # THE SECRET: Look for the report-TREB div with html attribute
            report_div = soup.select_one('div.report-TREB')
            
            if report_div and report_div.get('html'):
                # Unescape and parse the nested HTML
                unescaped_html = html.unescape(report_div['html'])
                inner_soup = BeautifulSoup(unescaped_html, 'html.parser')
                
                # Now extract from the inner HTML
                addr_tag = inner_soup.select_one('div.addr h1')
                price_tag = inner_soup.select_one('div.price h1 span[style*="color:darkblue"]')
                details_table = inner_soup.select_one('table.short-details')
                type_tag = inner_soup.select_one('div.addr h2')
                desc_tag = inner_soup.select_one('span.description.readmore')
                images = inner_soup.select('ul.photos-slideshow img.listing-photo')
            else:
                # Fallback to regular parsing
                addr_tag = soup.select_one('div.addr h1')
                price_tag = soup.select_one('div.price h1 span[style*="color:darkblue"]')
                details_table = soup.select_one('table.short-details')
                type_tag = soup.select_one('div.addr h2')
                desc_tag = soup.select_one('span.description.readmore')
                images = soup.select('ul.photos-slideshow img.listing-photo')
            
            # Extract data
            address = addr_tag.get_text(strip=True) if addr_tag else "Address Not Available"
            price = price_tag.get_text(strip=True) if price_tag else "Price Not Available"
            
            beds, baths, dom = "0", "0", "0"
            if details_table:
                for td in details_table.find_all('td'):
                    text = td.get_text(strip=True)
                    if 'Beds' in text: beds = text.replace('Beds', '').strip()
                    elif 'Baths' in text: baths = text.replace('Baths', '').strip()
                    elif 'dom' in text.lower(): dom = text.lower().replace('dom', '').strip()
            
            prop_type = type_tag.get_text(strip=True) if type_tag else "Residential"
            description = desc_tag.get_text(strip=True) if desc_tag else ""
            
            # Extract images
            image_urls = []
            for img in images:
                src = img.get('src') or img.get('data-src')
                if src:
                    if src.startswith('/'):
                        src = f"https://app.realmmlp.ca{src}"
                    image_urls.append(src)
            
            properties.append({
                'id': mls.lower(),
                'mls': mls,
                'address': address,
                'price': price,
                'beds': beds,
                'baths': baths,
                'dom': dom,
                'type': prop_type,
                'description': description,
                'images': image_urls,
                'status': 'Active'
            })
            
            time.sleep(1)
        
        # Save to JSON
        with open('properties.json', 'w') as f:
            json.dump(properties, f, indent=2)
        
        print(f"✅ Successfully scraped {len(properties)} properties!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    scrape_properties()
