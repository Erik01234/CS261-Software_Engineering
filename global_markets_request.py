# This code will give you the following response: https://www.alphavantage.co/query?function=MARKET_STATUS&apikey=demo
import requests
import json


api_key = "QC6PHJMTIZHC8S6B"
# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = f'https://www.alphavantage.co/query?function=MARKET_STATUS&apikey={api_key}'
r = requests.get(url)
data = r.json()

print(data)

# pretty_json = json.dumps(data, indent=4)
# print(pretty_json)