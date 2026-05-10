import cloudscraper
from bs4 import BeautifulSoup

scraper = cloudscraper.create_scraper()
resp = scraper.get('https://www.tgju.org/', timeout=15)
soup = BeautifulSoup(resp.text, 'html.parser')

# استخراج قیمت دلار (همان روش قبلی)
dollar_row = soup.find('tr', {'data-market-row': 'price_dollar_rl'})
if dollar_row:
    cell = dollar_row.find('td', class_='nf')
    if cell:
        print('دلار:', cell.text.strip().replace(',', ''))
else:
    print('دلار پیدا نشد')
