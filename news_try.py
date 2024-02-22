import requests
import logging
from datetime import datetime, timedelta
import json

def get_news(tickers, topic, sort, days_ago, limit):
    api_key = "QC6PHJMTIZHC8S6B"
    time_from = (datetime.utcnow() - timedelta(days=days_ago)).strftime('%Y%m%dT%H%M')

    # Construct the API URL with the dynamic 'time_from'
    url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={tickers}&topics={topic}&sort={sort}&time_from={time_from}&limit={limit}&apikey={api_key}'
    try:
        response = requests.get(url)
        response.raise_for_status()  # This will raise an exception for HTTP errors
        data = response.json()
        news_items = format_news_feed_data(data)
        return news_items
    except requests.exceptions.HTTPError as errh:
        logging.error("Http Error: %s", errh)
    except requests.exceptions.ConnectionError as errc:
        logging.error("Error Connecting: %s", errc)
    except requests.exceptions.Timeout as errt:
        logging.error("Timeout Error: %s", errt)
    except requests.exceptions.RequestException as err:
        logging.error("Other Error: %s", err)

def format_news_feed_data(data):
    articles = []
    for item in data.get('feed', []):
        try:
            publishedTime = datetime.strptime(item.get('time_published'), "%Y%m%dT%H%M%S")
        except ValueError:
            publishedTime = 'N/A'  # Handle incorrect format gracefully
        
        # Prepare ticker sentiment details if any
        ticker_sentiments = []
        for ticker_detail in item.get('ticker_sentiment', []):
            ticker_sentiment = {
                "ticker": ticker_detail.get('ticker', 'N/A'),
                "relevanceScore": ticker_detail.get('relevance_score', 'N/A'),
                "sentimentScore": ticker_detail.get('ticker_sentiment_score', 'N/A'),
                "sentimentLabel": ticker_detail.get('ticker_sentiment_label', 'N/A')
            }
            ticker_sentiments.append(ticker_sentiment)
        
        article = {
            "tickerID": ticker, 
            "title": item.get('title', 'N/A'),
            "url": item.get('url', 'N/A'),
            "publishedTime": publishedTime,
            "authors": item.get('authors', []),
            "summary": item.get('summary', 'N/A'),
            "bannerImageURL": item.get('banner_image', 'N/A'),
            "source": item.get('source', 'N/A'),
            "category": item.get('category_within_source', 'N/A'),
            "sourceDomain": item.get('source_domain', 'N/A'),
            "overallSentiment": item.get('overall_sentiment_label', 'N/A'),
            "tickerSentiments": ticker_sentiments
        }
        articles.append(article)
    return articles

ticker = "TSLA"  
news_items = get_news(ticker, '', 'RELEVANCE', 1, '5')
