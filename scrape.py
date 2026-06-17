import os
import requests
from bs4 import BeautifulSoup
import json
import re
import time

def scrape_properties():
    # The robot looks for the link you give it
    url = os.environ.get('TARGET_URL')
    if not url:
        print("No URL provided!")
        return
        
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        # The robot finds all the MLS numbers hidden in your link
        mls_numbers = re.findall(r'[A-Z]\d{8}', url.upper())
        mls_numbers = list(dict.fromkeys(mls_numbers))
        print(f"Found {len(mls_numbers)} MLS numbers in the link.")
        
        properties = []
        
        # The robot visits every single property page one by one
        for mls in mls_numbers:
            detail_url = f"https://app.realmmlp.ca/listings/TREB-{mls}"
            print(f"Scraping {detail_url}...")
            
            response = requests.get(detail_url, headers=headers)
            if response.status_code != 200:
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Grab the Address
            addr_tag = soup.select_one('div.addr h1')
            address = addr_tag.get_text(strip=True) if addr_tag else "Address Not Available"
            
            # Grab the Price
            price_tag = soup.select_one('div.price h1 span[style*="color:darkblue"]')
            price = price_tag.get_text(strip=True) if price_tag else "Price Not Available"
                
            # Grab Beds, Baths, and Days on Market
            beds, baths, dom = "0", "0", "0"
            details_table = soup.select_one('table.short-details')
            if details_table:
                for td in details_table.find_all('td'):
                    text = td.get_text(strip=True)
                    if 'Beds' in text: beds = text.replace('Beds', '').strip()
                    elif 'Baths' in text: baths = text.replace('Baths', '').strip()
                    elif 'dom' in text.lower(): dom = text.lower().replace('dom', '').strip()
                        
            # Grab the Property Type (Detached, Condo, etc.)
            type_tag = soup.select_one('div.addr h2')
            prop_type = type_tag.get_text(strip=True) if type_tag else "Residential"
            
            # Grab the Description
            desc_tag = soup.select_one('span.description.readmore')
            description = desc_tag.get_text(strip=True) if desc_tag else ""
            
            # Grab the High-Res Photos
            images = []
            for img in soup.select('ul.photos-slideshow img.listing-photo'):
                src = img.get('src') or img.get('data-src')
                if src:
                    if src.startswith('/'): src = f"https://app.realmmlp.ca{src}"
                    images.append(src)
                    
            # Put all this info into a neat little package
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
                'images': images,
                'status': 'Active'
            })
            
            # Wait 1 second so we don't overwhelm the website
            time.sleep(1) 
            
        # Save all the packages into a file called properties.json
        with open('properties.json', 'w') as f:
            json.dump(properties, f, indent=2)
        print(f"Successfully scraped {len(properties)} properties!")
        
    except Exception as e:
        print(f"Error scraping: {e}")

if __name__ == "__main__":
    scrape_properties()
