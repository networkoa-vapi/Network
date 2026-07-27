import urllib.request
import re

url = 'https://www.bluestarindia.com/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    html = urllib.request.urlopen(req).read().decode('utf-8')
    matches = re.findall(r'src="([^"]*logo[^"]*\.png|[^"]*logo[^"]*\.svg|[^"]*logo[^"]*\.jpg)"', html, re.IGNORECASE)
    print("Found logos:", matches)
    if matches:
        logo_url = matches[0]
        if logo_url.startswith('/'):
            logo_url = 'https://www.bluestarindia.com' + logo_url
        print("Downloading:", logo_url)
        urllib.request.urlretrieve(logo_url, r'C:\Network\static\company_logos\noa_erp_logo.png')
        urllib.request.urlretrieve(logo_url, r'C:\Network\media\company_logos\noa_erp_logo.png')
        print("Logo downloaded.")
except Exception as e:
    print("Error:", e)
