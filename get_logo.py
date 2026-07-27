import os
import django
import urllib.request
import re
from urllib.parse import urljoin

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'noa_erp.settings')
django.setup()

from core.models import Company
from django.core.files.base import ContentFile

url = 'http://www.noa.co.in/header.html'
html = urllib.request.urlopen(url, timeout=10).read().decode('utf-8', errors='ignore')

logo_url = 'http://www.noa.co.in/images/logo2.png'
print("Downloading logo from:", logo_url)
img_data = urllib.request.urlopen(logo_url).read()

c = Company.objects.get(name='Network Office Automation')
filename = 'noa_erp_logo.png'
c.logo.save(filename, ContentFile(img_data), save=True)
print("Logo saved to Company successfully.")

