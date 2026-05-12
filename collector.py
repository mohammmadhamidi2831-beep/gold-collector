import cloudscraper
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import os

CSV_FILE = "gold_data.csv"
scraper = cloudscraper.create_scraper()

def get_all_prices():
    """گرفتن همزمان دلار، طلا ۱۸ و انس جهانی از tgju.org"""
    try:
        resp = scraper.get('https://www.tgju.org/', timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')

        def extract_price(market_row):
            row = soup.find('tr', {'data-market-row': market_row})
            if row:
                cell = row.find('td', class_='nf')
                if cell:
                    return float(cell.text.strip().replace(',', ''))
            return None

        dollar = extract_price('price_dollar_rl')
        gold18 = extract_price('geram18') or extract_price('price_gold18')

        # گرفتن انس جهانی از لیست بالای صفحه
        ons_li = soup.find('li', id='1-ons')
        ons = None
        if ons_li:
            ons_span = ons_li.find('span', class_='info-price')
            if ons_span:
                ons = float(ons_span.text.strip().replace(',', ''))

        return dollar, gold18, ons
    except Exception as e:
        print(f"Error: {e}")
        return None, None, None

def compute_derived(ons, dollar):
    ons_toman = round(ons * dollar, 2) if (ons and dollar) else None
    gol18_calc = round((ons * dollar / 31.1035) * 0.75, 2) if (ons and dollar) else None
    gol17_calc = round((ons * dollar / 31.1035) * (17/24), 2) if (ons and dollar) else None
    return ons_toman, gol18_calc, gol17_calc

def save_to_csv(timestamp, ons, dollar, gold18, ons_toman, gol18_calc, gol17_calc):
    row = {
        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'ons_dollar': ons,
        'dollar_bazar': dollar,
        'gol18_bazar': gold18,
        'gol17_bazar': None,
        'ons_toman': ons_toman,
        'gol18_calc': gol18_calc,
        'gol17_calc': gol17_calc
    }
    df = pd.DataFrame([row])
    header = not os.path.exists(CSV_FILE)
    df.to_csv(CSV_FILE, mode='a', index=False, header=header)

def job():
    now = datetime.now()
    print(f"Running job at {now}")
    dollar, gold18, ons = get_all_prices()
    print(f"Ons: {ons}, Dollar: {dollar}, Gold18: {gold18}")

    if ons and dollar and gold18:
        ons_toman, gol18_calc, gol17_calc = compute_derived(ons, dollar)
        save_to_csv(now, ons, dollar, gold18, ons_toman, gol18_calc, gol17_calc)
        print("Data saved.\n")
    else:
        print("One of the prices is None. Skipping...\n")

if __name__ == "__main__":
    job()
