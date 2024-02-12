import requests
import logging
from configparser import ConfigParser

# Configuration Setup for Alpha Vantage API
config = ConfigParser()
config.read('config.ini')
api_key = config.get('alpha_api', 'api_key')
base_url = config.get('alpha_api', 'base_url')

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def global_markets_status():
    url = f'{base_url}query?function=MARKET_STATUS&apikey={api_key}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.HTTPError as errh:
        logging.error("Http Error: %s", errh)
    except requests.exceptions.ConnectionError as errc:
        logging.error("Error Connecting: %s", errc)
    except requests.exceptions.Timeout as errt:
        logging.error("Timeout Error: %s", errt)
    except requests.exceptions.RequestException as err:
        logging.error("Other Error: %s", err)


def format_global_market_status(stock_data):
    formatted_output = ""

    if stock_data:
        formatted_output += f"Endpoint: {stock_data.get('endpoint')}\n"
        for market in stock_data.get('markets', []):
            formatted_output += "\nMarket:\n"
            formatted_output += f"  Market Type: {market.get('market_type')}\n"
            formatted_output += f"  Region: {market.get('region')}\n"
            formatted_output += f"  Primary Exchanges: {market.get('primary_exchanges')}\n"
            formatted_output += f"  Local Open: {market.get('local_open')}\n"
            formatted_output += f"  Local Close: {market.get('local_close')}\n"
            formatted_output += f"  Current Status: {market.get('current_status')}\n"
            formatted_output += f"  Notes: {market.get('notes')}\n"

    return formatted_output

def top_gainers_losers():
    url = f'{base_url}query?function=TOP_GAINERS_LOSERS&apikey={api_key}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.HTTPError as errh:
        logging.error("Http Error: %s", errh)
    except requests.exceptions.ConnectionError as errc:
        logging.error("Error Connecting: %s", errc)
    except requests.exceptions.Timeout as errt:
        logging.error("Timeout Error: %s", errt)
    except requests.exceptions.RequestException as err:
        logging.error("Other Error: %s", err)

def format_gainers_losers(data):
    formatted_output = ""

    if data:
        formatted_output += f"Metadata: {data.get('metadata', 'N/A')}\n"
        formatted_output += f"Last Updated: {data.get('last_updated', 'N/A')}\n\n"

        formatted_output += "Top Gainers:\n"
        for gainer in data.get('top_gainers', []):
            formatted_output += format_ticker_info(gainer)

        formatted_output += "\nTop Losers:\n"
        for loser in data.get('top_losers', []):
            formatted_output += format_ticker_info(loser)

        formatted_output += "\nMost Actively Traded:\n"
        for active in data.get('most_actively_traded', []):
            formatted_output += format_ticker_info(active)

    return formatted_output

def format_ticker_info(ticker_info):
    return (f"  Ticker: {ticker_info.get('ticker', 'N/A')}, "
            f"Price: {ticker_info.get('price', 'N/A')}, "
            f"Change: {ticker_info.get('change_amount', 'N/A')}, "
            f"Change %: {ticker_info.get('change_percentage', 'N/A')}, "
            f"Volume: {ticker_info.get('volume', 'N/A')}\n")

def news(tickers, topic, sort, time_from, limit):#this method returns recent news about a given topic and other parameters.
    url = f'{base_url}query?function=NEWS_SENTIMENT&tickers={tickers}&topics={topic}&sort={sort}&time_from={time_from}&limit={limit}&apikey={api_key}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.HTTPError as errh:
        logging.error("Http Error: %s", errh)
    except requests.exceptions.ConnectionError as errc:
        logging.error("Error Connecting: %s", errc)
    except requests.exceptions.Timeout as errt:
        logging.error("Timeout Error: %s", errt)
    except requests.exceptions.RequestException as err:
        logging.error("Other Error: %s", err)

def format_news_feed_data(data):
    formatted_output = ""

    if data:
        formatted_output += f"Items: {data.get('items', 'N/A')}\n"
        formatted_output += f"Sentiment Score Definition: {data.get('sentiment_score_definition', 'N/A')}\n"
        formatted_output += f"Relevance Score Definition: {data.get('relevance_score_definition', 'N/A')}\n\n"

        for item in data.get('feed', []):
            formatted_output += format_news_item(item) + "\n\n"

    return formatted_output

def format_news_item(item):
    item_output = f"Title: {item.get('title', 'N/A')}\n"
    item_output += f"URL: {item.get('url', 'N/A')}\n"
    item_output += f"Published Time: {item.get('time_published', 'N/A')}\n"
    item_output += f"Authors: {', '.join(item.get('authors', []))}\n"
    item_output += f"Summary: {item.get('summary', 'N/A')}\n"
    item_output += f"Banner Image: {item.get('banner_image', 'N/A')}\n"
    item_output += f"Source: {item.get('source', 'N/A')}\n"
    item_output += f"Category: {item.get('category_within_source', 'N/A')}\n"
    item_output += f"Source Domain: {item.get('source_domain', 'N/A')}\n"
    item_output += f"Overall Sentiment: {item.get('overall_sentiment_label', 'N/A')} (Score: {item.get('overall_sentiment_score', 'N/A')})\n"
    
    # Format ticker sentiment details if any
    if 'ticker_sentiment' in item:
        item_output += "Ticker Sentiments:\n"
        for ticker in item['ticker_sentiment']:
            item_output += f"  - Ticker: {ticker.get('ticker', 'N/A')}, "
            item_output += f"Relevance Score: {ticker.get('relevance_score', 'N/A')}, "
            item_output += f"Sentiment Score: {ticker.get('ticker_sentiment_score', 'N/A')}, "
            item_output += f"Label: {ticker.get('ticker_sentiment_label', 'N/A')}\n"

    return item_output

# General usage for the news feed method
if __name__ == "__main__":
    news_feed = format_news_feed_data(news('IBM','','RELEVANCE','','5')) # tickers, topic, sort, time_from, limit
    print(news_feed)