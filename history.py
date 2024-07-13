import uuid
import kalshi_python
import json
import time
from datetime import datetime
from datetime import timedelta
from pprint import pprint

config = kalshi_python.Configuration()
config.host = 'https://demo-api.kalshi.co/trade-api/v2'
last_api_call = datetime.now()

kalshi_api = kalshi_python.ApiInstance(
    email='email@email.com',
    password='12345',
    configuration=config,
)

def rate_limit():
    global last_api_call
    THRESHOLD_IN_MILLISECONDS = 100

    now = datetime.now()
    threshold_in_microseconds = 1000 * THRESHOLD_IN_MILLISECONDS
    threshold_in_seconds = THRESHOLD_IN_MILLISECONDS / 1000
    if now - last_api_call < timedelta(microseconds=threshold_in_microseconds):
        time.sleep(threshold_in_seconds)
    last_api_call = datetime.now()

# setup
eventsReponse = kalshi_api.get_events()
marketsResponse = kalshi_api.get_markets()

events = eventsReponse.__dict__["_events"]
markets = marketsResponse.__dict__["_markets"]
eventTickers = [event.__dict__['_event_ticker'] for event in events]
marketTickers = [market.__dict__['_ticker'] for market in markets]

eventData, marketData, orderbookData, historyData = [], [], [], []

print("GETTING EVENT && MARKET DATA")
for ticker in eventTickers:
    rate_limit()
    eventResponse = kalshi_api.get_event(ticker)
    eventData.append(eventResponse.__dict__["_event"].__dict__)
    markets = { ticker: [] }
    for market in eventResponse.__dict__["_markets"]:
        markets[ticker].append(market.__dict__)
    marketData.append(markets)

with open("event_data.json", 'w') as json_file:
    json_string = json.dumps(eventData, indent=4)
    json_file.write(json_string)

with open("market_data.json", 'w') as json_file:
    json_string = json.dumps(marketData, indent=4)
    json_file.write(json_string)

print("GETTING ORDERBOOK DATA")
for ticker in marketTickers:
    rate_limit()
    orderbookResponse = kalshi_api.get_market_orderbook(ticker)
    output = {}
    output[ticker] = orderbookResponse.__dict__["_orderbook"].__dict__
    orderbookData.append(output)

with open("orderbook_data.json", 'w') as json_file:
    json_string = json.dumps(orderbookData, indent=4)
    json_file.write(json_string)

print("GETTING MARKET HISTORY DATA")
for ticker in marketTickers:
    rate_limit()
    historyResponse = kalshi_api.get_market_history(ticker)
    orderbooks = { ticker: [] }
    for history in historyResponse.__dict__["_history"]:
        orderbooks[ticker].append(history.__dict__)
    historyData.append(orderbooks)

with open("market_history.json", 'w') as json_file:
    json_string = json.dumps(historyData, indent=4)
    json_file.write(json_string)

pprint("Finished cooking the JSON files big bro")
