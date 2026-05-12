import cloudscraper
from bs4 import BeautifulSoup

scraper = cloudscraper.create_scraper()
resp = scraper.get('https://alanchand.com/', timeout=15)
soup = BeautifulSoup(resp.text, 'html.parser')

# چاپ برچسب قیمت‌های اصلی (معمولاً داخل div با کلاس price)
for div in soup.find_all('div', class_='price'):
    print(div.get_text(strip=True))

# اگر کلاس خاصی برای دلار هست، اونها رو هم چاپ کن
for span in soup.find_all('span', class_='value'):
    print(span.get_text(strip=True))
