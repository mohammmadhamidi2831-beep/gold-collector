import requests

def get_price_from_api(symbol):
    url = f"https://api.tgju.org/api/v1/market/indicator/summary/{symbol}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(url, headers=headers, timeout=10)
    data = resp.json()
    # ساختار پاسخ: {'response': {'indicator': {'price': ...}}}
    price = data['response']['indicator']['price']
    return price

dollar = get_price_from_api('price_dollar_rl')
gold18 = get_price_from_api('geram18')
print("دلار:", dollar)
print("طلای ۱۸:", gold18)
