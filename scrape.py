import os
from bs4 import BeautifulSoup
import json
import re
import html

def scrape_properties():
    # Check if the file you uploaded exists
    if not os.path.exists('source.html'):
        print("❌ source.html not found! Please upload it first.")
        return
        
    print("📂 Reading your downloaded file...")
    with open('source.html', 'r', encoding='utf-8') as f:
        page_content = f.read()
        
    soup = BeautifulSoup(page_content, 'html.parser')
    properties = []
    
    # The website hides data in a special "report-TREB" box
    report_div = soup.select_one('div.report-TREB')
    
    if report_div and report_div.get('html'):
        print(" Found the secret data box!")
        unescaped_html = html.unescape(report_div['html'])
        inner_soup = BeautifulSoup(unescaped_html, 'html.parser')
        
        # Now we extract the data from inside that box
        addr_tag = inner_soup.select_one('div.addr h1')
        price_tag = inner_soup.select_one('div.price h1 span[style*="color:darkblue"]')
        details_table = inner_soup.select_one('table.short-details')
        type_tag = inner_soup.select_one('div.addr h2')
        
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
        
        # Since this is just one property from the file, we add it
        # (Note: If your source.html has multiple properties, we would loop here)
        properties.append({
            'id': 'manual-1',
            'mls': 'Manual',
            'address': address,
            'price': price,
            'beds': beds,
            'baths': baths,
            'dom': dom,
            'type': prop_type,
            'description': '',
            'images': [],
            'status': 'Active'
        })
    else:
        print("️ Could not find the data box. The file might be formatted differently.")
        # Fallback: Try to find any price on the page
        all_text = soup.get_text()
        prices = re.findall(r'\$[\d,]+', all_text)
        if prices:
            print(f"Found prices in text: {prices[:5]}...")

    # Save whatever we found
    with open('properties.json', 'w') as f:
        json.dump(properties, f, indent=2)
    print(f"✅ Saved {len(properties)} properties from your file!")

if __name__ == "__main__":
    scrape_properties()
