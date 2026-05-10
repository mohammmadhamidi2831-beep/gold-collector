import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
import yfinance as yf
from datetime import datetime
import os

# --------------------------------------------
# تنظیمات
# --------------------------------------------
CSV_FILE = "gold_data.csv"

# --------------------------------------------
# ۱. گرفتن انس جهانی طلا (XAU/USD) با yfinance
# --------------------------------------------
def get_ons_dollar():
    try:
        gold = yf.Ticker("GC=F")
        data = gold.history(period="1d", interval="1m")
        if not data.empty:
            last_price = data['Close'].iloc[-1]
            return round(last_price, 2)
        else:
            return gold.info.get('regularMarketPreviousClose', None)
    except Exception as e:
        print(f"Error getting gold price: {e}")
        return None

# --------------------------------------------
# ۲. اسکرپینگ قیمت‌های داخلی از tgju.org
# --------------------------------------------
def get_iran_prices():
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = "https://www.tgju.org/"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')

        def extract_price(soup, market_row):
            row = soup.find('tr', {'data-market-row': market_row})
            if row:
                cell = row.find('td', class_='nf')
                if cell:
                    return float(cell.text.strip().replace(',', ''))
            return None

        dollar = extract_price(soup, 'price_dollar_rl')
        gold18 = extract_price(soup, 'geram18') or extract_price(soup, 'price_gold18')
        gold17 = None

        return dollar, gold18, gold17

    except Exception as e:
        print(f"Scraping error: {e}")
        return None, None, None

# --------------------------------------------
# ۳. محاسبات فیچرهای مهندسی‌شده
# --------------------------------------------
def compute_derived(ons_dollar, dollar_bazar, gold18_bazar, gold17_bazar):
    ons_toman = round(ons_dollar * dollar_bazar, 2) if (ons_dollar and dollar_bazar) else None
    gol18_calc = round((ons_dollar * dollar_bazar / 31.1035) * 0.75, 2) if (ons_dollar and dollar_bazar) else None
    gol17_calc = round((ons_dollar * dollar_bazar / 31.1035) * (17/24), 2) if (ons_dollar and dollar_bazar) else None
    return ons_toman, gol18_calc, gol17_calc

# --------------------------------------------
# ۴. ذخیره‌سازی در CSV
# --------------------------------------------
def save_to_csv(timestamp, ons_dollar, dollar, gold18_bazar, gold17_bazar, ons_toman, gol18_calc, gol17_calc):
    row = {
        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'ons_dollar': ons_dollar,
        'dollar_bazar': dollar,
        'gol18_bazar': gold18_bazar,
        'gol17_bazar': gold17_bazar,
        'ons_toman': ons_toman,
        'gol18_calc': gol18_calc,
        'gol17_calc': gol17_calc
    }
    df = pd.DataFrame([row])
    header = not os.path.exists(CSV_FILE)
    df.to_csv(CSV_FILE, mode='a', index=False, header=header)

# --------------------------------------------
# ۵. تابع اصلی
# --------------------------------------------
def job():
    now = datetime.now()
    print(f"Running job at {now}")

    ons = get_ons_dollar()
    print(f"Ons: {ons}")

    dollar, gol18, gol17 = get_iran_prices()
    print(f"Dollar: {dollar}, Gold18: {gol18}, Gold17: {gol17}")

    if ons is None or dollar is None or gol18 is None:
        print("One of the prices is None. Skipping...")
    else:
        ons_toman, gol18_calc, gol17_calc = compute_derived(ons, dollar, gol18, gol17)
        save_to_csv(now, ons, dollar, gol18, gol17, ons_toman, gol18_calc, gol17_calc)
        print("Data saved.\n")

if __name__ == "__main__":
    job()
