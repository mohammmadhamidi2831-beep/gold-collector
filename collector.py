import cloudscraper
import pandas as pd
import requests
from bs4 import BeautifulSoup
import yfinance as yf
from datetime import datetime
import os

CSV_FILE = "gold_data.csv"

# --- ۱. انس جهانی با yfinance ---
def get_ons_dollar():
    try:
        gold = yf.Ticker("GC=F")
        data = gold.history(period="1d", interval="1m")
        if not data.empty:
            return round(data['Close'].iloc[-1], 2)
        else:
            return gold.info.get('regularMarketPreviousClose', None)
    except:
        return None

# --- ۲. قیمت‌های داخلی با cloudscraper ---
def get_iran_prices():
    try:
        scraper = cloudscraper.create_scraper()
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
        return dollar, gold18, None
    except:
        return None, None, None

# --- ۳. محاسبات ---
def compute_derived(ons, dollar, gold18, gold17):
    ons_toman = round(ons * dollar, 2) if (ons and dollar) else None
    gol18_calc = round((ons * dollar / 31.1035) * 0.75, 2) if (ons and dollar) else None
    gol17_calc = round((ons * dollar / 31.1035) * (17/24), 2) if (ons and dollar) else None
    return ons_toman, gol18_calc, gol17_calc

# --- ۴. ذخیره‌سازی ---
def save_to_csv(timestamp, ons, dollar, gold18, gold17, ons_toman, gol18_calc, gol17_calc):
    row = {
        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'ons_dollar': ons,
        'dollar_bazar': dollar,
        'gol18_bazar': gold18,
        'gol17_bazar': gold17,
        'ons_toman': ons_toman,
        'gol18_calc': gol18_calc,
        'gol17_calc': gol17_calc
    }
    df = pd.DataFrame([row])
    header = not os.path.exists(CSV_FILE)
    df.to_csv(CSV_FILE, mode='a', index=False, header=header)

# --- ۵. اجرای اصلی ---
def job():
    now = datetime.now()
    print(f"Running job at {now}")

    ons = get_ons_dollar()
    print(f"Ons: {ons}")

    dollar, gold18, gold17 = get_iran_prices()
    print(f"Dollar: {dollar}, Gold18: {gold18}")

    if ons and dollar and gold18:
        ons_toman, gol18_calc, gol17_calc = compute_derived(ons, dollar, gold18, gold17)
        save_to_csv(now, ons, dollar, gold18, gold17, ons_toman, gol18_calc, gol17_calc)
        print("Data saved.\n")
    else:
        print("One of the prices is None. Skipping...\n")

if __name__ == "__main__":
    job()
