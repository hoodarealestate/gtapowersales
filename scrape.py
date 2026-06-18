import os
import requests
from bs4 import BeautifulSoup
import json
import re

def scrape_properties():
    url = os.environ.get('TARGET_URL')
    print(f"🎯 Starting scraper for: {url[:50]}...")
    
    if not url:
        print("❌ ERROR: No URL provided!")
        return
        
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        print(f"📥 Fetching page...")
        response = requests.get(url, headers=headers, timeout=30)
        print(f"📊 Response status: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for ANY element that might contain property data
        all_divs = soup.find_all('div')
        print(f"🔍 Found {len(all_divs)} div elements to check")
        
        properties = []
        
        # Look for patterns that indicate property listings
        for i, div in enumerate(all_divs):
            text = div.get_text()
            
            # Look for price patterns ($XXX,XXX or $X.XXM)
            if re.search(r'\$[\d,]+', text):
                # This might be a property listing!
                print(f"💰 Found potential property at div #{i}")
                
                # Try to extract MLS number
                mls_match = re.search(r'[A-Z]\d{8}', text)
                mls = mls_match.group(0) if mls_match else f"prop-{i}"
                
                # Try to extract price
                price_match = re.search(r'\$[\d,]+', text)
                price = price_match.group(0) if price_match else "Price Not Available"
                
                # Try to extract address (look for text with comma, usually street, city)
                lines = text.split('\n')
                address = "Address Not Available"
                for line in lines:
                    line = line.strip()
                    if ',' in line and len(line) > 10 and len(line) < 100 and '$' not in line:
                        address = line
                        break
                
                # Try to extract beds/baths
                beds_match = re.search(r'(\d+)\s*Bed', text, re.IGNORECASE)
                baths_match = re.search(r'(\d+)\s*Bath', text, re.IGNORECASE)
                
                beds = beds_match.group(1) if beds_match else "0"
                baths = baths_match.group(1) if baths_match else "0"
                
                # Only add if we found at least a price
                if price != "Price Not Available":
                    properties.append({
                        'id': mls.lower(),
                        'mls': mls,
                        'address': address,
                        'price': price,
                        'beds': beds,
