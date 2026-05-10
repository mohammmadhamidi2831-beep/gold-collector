import requests
from bs4 import BeautifulSoup

url = "https://bonbast.com/"
headers = {'User-Agent': 'Mozilla/5.0'}
resp = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(resp.text, 'html.parser')

# چاپ کلاس‌های اصلی
for td in soup.find_all('td'):
    print(td.get_text(strip=True))
