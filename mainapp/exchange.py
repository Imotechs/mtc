import requests
import json
access_key = 'G2I6ugLl8WOuFpRqSDfuzLqB4IPE0rAI'

payload = {}
headers= {
  "apikey": access_key
}
def convert_currency(currency,amount):
    to = 'USD'
    usd_from = currency
    print(usd_from)
    url = f"https://api.apilayer.com/exchangerates_data/convert?to={to}&from={usd_from}&amount={amount}"
    response = requests.request("GET", url, headers=headers, data = payload)
    status_code = response.status_code
    result = json.loads(response.text)
    if status_code == 200:
      return result['result']
    return result

