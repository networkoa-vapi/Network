import requests
from bs4 import BeautifulSoup
import json

def fetch_bluestar_products():
    url = "https://shop.bluestarindia.com/collections/split-ac"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            print("Title:", soup.title.text)
            
            # Find products. Usually Shopify sites (which it likely is) have .grid-product or similar
            items = soup.find_all('div', class_='grid-product')
            if not items:
                items = soup.find_all('div', class_='product-item')
            if not items:
                items = soup.find_all('a', class_='grid-view-item__link')
            
            print(f"Found {len(items)} possible product blocks.")
            
            # If Shopify, we might find a script tag with JSON
            for idx, script in enumerate(soup.find_all('script', type='application/json')):
                print(f"JSON Script {idx} found")
            
            return "Success"
        else:
            return f"Failed with status: {response.status_code}"
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    print(fetch_bluestar_products())
