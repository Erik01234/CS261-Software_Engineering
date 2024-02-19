# This code will give you the following response: https://www.alphavantage.co/query?function=MARKET_STATUS&apikey=demo
import requests
import json


api_key = "QC6PHJMTIZHC8S6B"
# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = f'https://www.alphavantage.co/query?function=MARKET_STATUS&apikey={api_key}'
r = requests.get(url)
data = r.json()

print(data)

def split_primary_exchanges(json_data):
    new_markets = []
    for market in json_data['markets']:
        exchanges = market['primary_exchanges'].split(', ')
        for exchange in exchanges:
            new_market = market.copy()  # Copy the original market dictionary
            new_market['primary_exchanges'] = exchange  # Replace with the single exchange
            new_markets.append(new_market)
    return new_markets

# Use the function and store the result
split_markets = split_primary_exchanges(data)

# print(split_markets)
# Print the result or process it further
for market in split_markets:
    print(json.dumps(market, indent=4))