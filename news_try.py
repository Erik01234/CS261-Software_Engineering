import requests
import logging
from datetime import datetime, timedelta
import json

def get_news_for_ticker(ticker, topic, sort, days_ago, limit):
    api_key = "QC6PHJMTIZHC8S6B"
    time_from = (datetime.utcnow() - timedelta(days=days_ago)).strftime('%Y%m%dT%H%M')
    
    # Construct the API URL with the dynamic 'time_from'
    url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&topics={topic}&sort={sort}&time_from={time_from}&limit={limit}&apikey={api_key}'
    try:
        response = requests.get(url)
        response.raise_for_status()  # This will raise an exception for HTTP errors
        data = response.json()
        news_items = format_news_feed_data_for_ticker(data, ticker)
        return news_items
    except requests.exceptions.HTTPError as errh:
        logging.error("Http Error: %s", errh)
    except requests.exceptions.ConnectionError as errc:
        logging.error("Error Connecting: %s", errc)
    except requests.exceptions.Timeout as errt:
        logging.error("Timeout Error: %s", errt)
    except requests.exceptions.RequestException as err:
        logging.error("Other Error: %s", err)

def format_news_feed_data_for_ticker(data, ticker):
    articles = []
    for item in data.get('feed', []):
        try:
            publishedTime = datetime.strptime(item.get('time_published'), "%Y%m%dT%H%M%S").strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            publishedTime = 'N/A'  # Handle incorrect format gracefully
        article = {
            "tickerID": ticker,
            "url": item.get('url', 'N/A'),
            "publishedTime": publishedTime,
            "summary": item.get('summary', 'N/A'),
            "bannerImageURL": item.get('banner_image', 'N/A'),
            "source": item.get('source', 'N/A'),
            "category": item.get('category_within_source', 'N/A'),
            "sourceDomain": item.get('source_domain', 'N/A'),
            "overallSentiment": item.get('overall_sentiment_label', 'N/A')
        }
        articles.append(article)
    return articles

ticker = "AAPL"  # Specify the ticker you are interested in
# Now calling the function with adjusted parameters for last 7 days and sorting by relevance
news_items = get_news_for_ticker(ticker, '', 'RELEVANCE', 1, '5') 
print(json.dumps(news_items, indent=4))
