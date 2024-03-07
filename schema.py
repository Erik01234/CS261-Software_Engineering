from sqlalchemy import create_engine, Column, Time
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from sqlalchemy import ForeignKey, Time
import datetime
from datetime import datetime, timedelta
import pandas as pd
import requests
import json
import logging
import csv

db = SQLAlchemy()

import requests


def custom_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    else:
        raise TypeError("Type not serializable")
    

def get_static_company_info(ticker):
    API_KEY = 'QC6PHJMTIZHC8S6B'  # Replace with your actual AlphaVantage API key
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={API_KEY}'
    
    response = requests.get(url)
    data = response.json()
    
    # Check if the response contains company information
    if not data:
        return 0

    # Extract the static information
    static_info = {
        'Symbol': ticker,
        'Name': data.get('Name'),
        'Exchange': data.get('Exchange'),
        'Currency': data.get('Currency'),
        'Country': data.get('Country'),
        'Address': data.get('Address'),
        'Description': data.get('Description'),
        'Sector': data.get('Sector'),
        'Industry': data.get('Industry')
    }

    print(static_info)
    
    return static_info

def get_current_stock_price_and_volume(ticker):
    API_KEY = 'QC6PHJMTIZHC8S6B'
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={API_KEY}"
    
    response = requests.get(url)
    data = response.json()
    
    if "Global Quote" in data:
        global_quote = data["Global Quote"]
        current_price = global_quote.get("05. price")
        current_volume = global_quote.get("06. volume")

        if current_price != None and current_volume != None:
        
            print({"Current Price": current_price, "Current Volume": current_volume})
            return {
                "Current Price": current_price,
                "Current Volume": current_volume
            }
        else:
            return 0
    else:
        return 0

def get_company_overview(ticker):
    API_KEY = 'QC6PHJMTIZHC8S6B'  # Replace with your actual AlphaVantage API key
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={API_KEY}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        data = response.json()
        
        if 'Error Message' in data:
            return 0
        
        # Extract the relevant information
        overview_data = {
            'MarketCapitalization': data.get('MarketCapitalization'),
            'PERatio': data.get('PERatio'),
            'EPS': data.get('EPS'),
            'ROE': data.get('ReturnOnEquityTTM'),
        }

        if overview_data:
            print(ticker)
            print(overview_data)
            return overview_data
        else:
            return 0
    
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except Exception as err:
        return f"An error occurred: {err}"

def get_global_market():
    api_key = "QC6PHJMTIZHC8S6B"
    url = f'https://www.alphavantage.co/query?function=MARKET_STATUS&apikey={api_key}'
    r = requests.get(url)
    data = r.json()
    if data != None:
        return data
    else:
        return 0
    
def getTopGainersLosers():
    api_key = "QC6PHJMTIZHC8S6B"
    url = f'https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={api_key}'
    r = requests.get(url)
    data = r.json()
    if data != None:
        return data
    else:
        return 0

companies = pd.read_csv('SP_500.csv')

tickers = companies['Symbol'].unique()

def get_news(tickers, topic, sort, days_ago, limit):
    api_key = "QC6PHJMTIZHC8S6B"
    time_from = (datetime.utcnow() - timedelta(days=days_ago)).strftime('%Y%m%dT%H%M')

    # Construct the API URL with the dynamic 'time_from'
    url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={tickers}&topics={topic}&sort={sort}&time_from={time_from}&limit={limit}&apikey={api_key}'
    try:
        response = requests.get(url)
        response.raise_for_status()  # This will raise an exception for HTTP errors
        data = response.json()
        news_items = format_news_feed_data(data, tickers)
        return news_items
    except requests.exceptions.HTTPError as errh:
        logging.error("Http Error: %s", errh)
    except requests.exceptions.ConnectionError as errc:
        logging.error("Error Connecting: %s", errc)
    except requests.exceptions.Timeout as errt:
        logging.error("Timeout Error: %s", errt)
    except requests.exceptions.RequestException as err:
        logging.error("Other Error: %s", err)

def format_news_feed_data(data, tickers):
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
            "tickerID": tickers, 
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

# Now calling the function with adjusted parameters for last 7 days and sorting by relevance


class Users(db.Model):
    #constant updates - dynamic
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text())
    hashed_password = db.Column(db.Text())
    token = db.Column(db.Text())
    isactivated = db.Column(db.Integer)

    def __init__(self, email, hashed_password, token, isactivated):
        self.email = email
        self.hashed_password = hashed_password
        self.token = token
        self.isactivated = isactivated


class Company(db.Model):
    #static table 
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String)
    name = db.Column(db.Text())
    sector = db.Column(db.Text())
    industry = db.Column(db.Text())
    exchange = db.Column(db.String)
    currency = db.Column(db.String)
    country = db.Column(db.String)
    address = db.Column(db.Text())
    description = db.Column(db.Text())


    def __init__(self, ticker, name, sector, industry, exchange, currency, country, address, description):
        self.name = name
        self.ticker = ticker
        self.sector = sector
        self.industry = industry
        self.exchange = exchange
        self.currency = currency
        self.country = country
        self.address = address
        self.description = description

class UserCompany(db.Model): 
    #constant updates - dynamic
    __tablename__ = 'usercompany'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Text())
    company = db.Column(db.Text())

    def __init__(self, user, company):
        self.user = user
        self.company = company


class Articles(db.Model):
    #constant updates - PERIODIC/DYNAMIC???
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    tickerID = db.Column(db.Integer)
    title = db.Column(db.Text)
    url = db.Column(db.String(255))
    publishedTime = db.Column(db.DateTime)
    authors = db.Column(db.String(255))
    summary = db.Column(db.Text())
    bannerImageURL = db.Column(db.String(255))
    source = db.Column(db.String(255))
    category = db.Column(db.String(255))
    sourceDomain = db.Column(db.String(255))
    overallSentiment = db.Column(db.String(50))

    def __init__(self, tickerID, title, url, publishedTime, authors, summary, bannerImageURL, source, category, sourceDomain, overallSentiment):
        self.url = url
        self.tickerID = tickerID
        self.title = title
        self.authors = authors
        self.publishedTime = publishedTime
        self.summary = summary
        self.bannerImageURL = bannerImageURL
        self.source = source
        self.category = category
        self.sourceDomain = sourceDomain
        self.overallSentiment = overallSentiment

    
class ArticleTickers(db.Model):
    #constant updates - dynamic
    __tablename__ = 'articletickers'
    id = db.Column(db.Integer, primary_key=True)
    articleID = db.Column(db.Integer, db.ForeignKey('articles.id'))
    tickerID = db.Column(db.Integer, db.ForeignKey('company.ticker'))
    relevanceScore = db.Column(db.Float(precision=25))
    sentimentScore = db.Column(db.Float(precision=25))

    def __init__(self, articleID, tickerID, relevanceScore, sentimentScore):
        self.articleID = articleID
        self.tickerID = tickerID
        self.relevanceScore = relevanceScore
        self.sentimentScore = sentimentScore

class TopGainers(db.Model):
    #constant updates - PERIODIC
    __tablename__ = 'topgainers'
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10))
    price = db.Column(db.Float(precision=6))
    change = db.Column(db.Float(precision=6))
    changePercent = db.Column(db.Float(precision=6))
    volume = db.Column(db.Float)

    def __init__(self, ticker, price, change, changePercent, volume):
        self.ticker = ticker
        self.price = price
        self.change = change
        self.changePercent = changePercent
        self.volume = volume

class TopLosers(db.Model):
    #constant updates - PERIODIC
    __tablename__ = 'toplosers'
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10))
    price = db.Column(db.Float(precision=6))
    change = db.Column(db.Float(precision=6))
    changePercent = db.Column(db.Float(precision=6))
    volume = db.Column(db.Float)

    def __init__(self, ticker, price, change, changePercent, volume):
        self.ticker = ticker
        self.price = price
        self.change = change
        self.changePercent = changePercent
        self.volume = volume


class ActivelyTraded(db.Model):
    #constant updates - PERIODIC -
    __tablename__ = 'activelytraded'
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10))
    price = db.Column(db.Float(precision=6))
    change = db.Column(db.Float(precision=6))
    changePercent = db.Column(db.Float(precision=6))
    volume = db.Column(db.Float)

    def __init__(self, ticker, price, change, changePercent, volume):
        self.ticker = ticker
        self.price = price
        self.change = change
        self.changePercent = changePercent
        self.volume = volume

class GlobalMarket(db.Model):
    #static, but based on closing time, we potentially have to modify status
    __tablename__ = "globalmarket"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20))
    region = db.Column(db.String(20))
    exchanges = db.Column(db.String(20))
    open = db.Column(db.Time)
    close = db.Column(db.Time)
    status = db.Column(db.String(10))
    notes = db.Column(db.Text())

    def __init__(self, type, region, exchanges, open, close, status, notes):
        self.type = type
        self.region = region
        self.exchanges = exchanges
        self.open = open
        self.close = close
        self.status = status
        self.notes = notes


class FinancialData(db.Model):
    #constant updates - PERIODIC (daily) - done in server.py
    __tablename__ = "financialdata"
    id = db.Column(db.Integer, primary_key=True)
    tickerID = db.Column(db.String, db.ForeignKey('company.ticker'))
    date = db.Column(db.DateTime) # update once a day
    marketCap = db.Column(db.Numeric) # market capitalisation
    pe_ratio = db.Column(db.Numeric) # price to earnings ratio
    eps = db.Column(db.Numeric) # earnings per share
    roe = db.Column(db.Numeric) # return on equity

    def __init__(self, tickerID, date, marketCap, pe_ratio, eps, roe):
        self.marketCap = marketCap
        self.tickerID = tickerID
        self.pe_ratio = pe_ratio
        self.eps = eps
        self.roe = roe
        self.date = date

class CurrentStockPrice(db.Model):
    #constant updates - PERIODIC (5 minutes) - done in server.py
    __tablename__ = "currentstockprice"
    id = db.Column(db.Integer, primary_key=True)
    tickerID = db.Column(db.String, db.ForeignKey('company.ticker'))
    timestamp = db.Column(db.DateTime) # update every 5 minutes
    stockPrice = db.Column(db.Numeric)
    volumeOfTrade = db.Column(db.Integer)

    def __init__(self, tickerID, timestamp, stockPrice, volumeOfTrade):
        self.stockPrice = stockPrice
        self.volumeOfTrade = volumeOfTrade
        self.tickerID = tickerID
        self.timestamp = timestamp

class SavedArticles(db.Model):
    __tablename__ = "savedarticles"
    id = db.Column(db.Integer, primary_key="True")
    userID = db.Column(db.Integer)
    articleID = db.Column(db.Integer)

    def __init__(self, userID, articleID):
        self.userID = userID
        self.articleID = articleID


def dbinit():
    pwdadmin = generate_password_hash("admin")
    pwderik = generate_password_hash("fasz")
    user_list = [
        Users("admin", pwdadmin, "x", 1),
        Users("rikifekete2003@gmail.com", pwderik, "x", 1)
        ]
    db.session.add_all(user_list)
    db.session.commit()

    user_company = [
        UserCompany(1, "AMD")
    ]
    db.session.add_all(user_company)
    db.session.commit()
        

    #DO NOT UNCOMMENT
    '''with open('financialdata.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        #writer.writerow([tickerOverview, datetime.now(), str(overview["MarketCapitalization"]), overview["PERatio"], overview["EPS"], overview["ROE"]])
        for tickerOverview in tickers:
            overview = get_company_overview(tickerOverview)
            if isinstance(overview, dict):
                if overview != 0:
                    writer.writerow([tickerOverview, datetime.now(), overview["MarketCapitalization"], overview["PERatio"], overview["EPS"], overview["ROE"]])'''
    

    with open('companies.csv', 'r') as file: 
        #read static company data from the companies.csv file
        csvreader = csv.reader(file)
        for row in csvreader:
            db.session.add(Company(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
            db.session.commit()

    
    with open('financialdata.csv', 'r') as file: 
        #read static financial data from the financialdata.csv file
        csvreader = csv.reader(file)
        for row in csvreader:
            #there is a common pattern of entries/records in the CSV file
            #all records in the CSV are string since it doesn't contain specific types
            #so instead of null values, it is an empty string OR None as a string 
            #the pattern is: either marketCap is None (as a string), and all other values are correct OR the ticker and date is non-empty, everything else is empty, OR all values are non-empty which is most optimal
            print("Column 3 VALUE IS "+row[3])
            if row[3] == "None":
                if row[4] != "": 
                    #if the marketCap is a None string AND all other values are non-empty (based on our observation), replace it with "0" and keep our other values
                    db.session.add(FinancialData(row[0], datetime.now(), row[2], 0, row[4], row[5]))
            elif row[2] == "":
                if row[3] == "":
                    #if all values but the ticker and datetime are empty, replace with default, type-specific null values
                    #COULD/SHOULD SKIP THESE KINDS OF RECORDS
                    db.session.add(FinancialData(row[0], datetime.now(), 0, 0, 0, 0))
            else:
                #else keep everything as is, updating with current timestamp 
                db.session.add(FinancialData(row[0], datetime.now(), row[2], row[3], row[4], row[5]))
            db.session.commit()

    
    '''for tickerOverview in tickers:
        overview = get_company_overview(tickerOverview)
        if overview != 0:
            db.session.add(FinancialData(tickerOverview, datetime.now(), overview["MarketCapitalization"], overview["PERatio"], overview["EPS"], overview["ROE"]))
    db.session.commit()'''




    
    for tickerStock in tickers:
        stockPriceList = get_current_stock_price_and_volume(tickerStock)
        if stockPriceList != 0:
            db.session.add(CurrentStockPrice(tickerStock, datetime.now(), stockPriceList["Current Price"], stockPriceList["Current Volume"]))
            db.session.commit()
    
    
    # Use the function and store the result
    split_markets = split_primary_exchanges(get_global_market())
    marketList = split_markets
    for market in marketList:
        print(market)
        if market != 0 and market != None:
            open_time = datetime.strptime(market['local_open'], "%H:%M").time()
            close_time = datetime.strptime(market['local_close'], "%H:%M").time()
            db.session.add(GlobalMarket(market["market_type"], market["region"], market["primary_exchanges"], open_time, close_time, market["current_status"], market["notes"]))
            db.session.commit()
            print("Inserted into Global Markets table!")
    
    topGainersLosersDict = getTopGainersLosers()
    topGainers = topGainersLosersDict["top_gainers"]
    topLosers = topGainersLosersDict["top_losers"]
    activelyTraded = topGainersLosersDict["most_actively_traded"]
    for gainers in topGainers:
        if gainers != None and gainers != 0:
            print(gainers)
            percent_float = float(gainers["change_percentage"].rstrip('%'))
            db.session.add(TopGainers(gainers["ticker"], gainers["price"], gainers["change_amount"], percent_float, gainers["volume"]))
            db.session.commit()
    
    for losers in topLosers:
        if losers != None and losers != 0:
            print(losers)
            percent_float = float(losers["change_percentage"].rstrip('%'))
            db.session.add(TopLosers(losers["ticker"], losers["price"], losers["change_amount"], percent_float, losers["volume"]))
            db.session.commit()

    for active in activelyTraded:
        if active != None and active != 0:
            print(active)
            percent_float = float(active["change_percentage"].rstrip('%'))
            db.session.add(ActivelyTraded(active["ticker"], active["price"], active["change_amount"], percent_float, active["volume"]))
            db.session.commit()
    
    
            
    for tickerNews in tickers:
        news_item = get_news(tickerNews, '', 'RELEVANCE', 1, '5')
        if news_item:
            for newsEntry in news_item:
                if newsEntry:
                    print(json.dumps(newsEntry, default=custom_serializer, indent=4))
                    authorArr = newsEntry["authors"]
                    authorString = ', '.join(authorArr)
                    news = Articles(newsEntry["tickerID"], newsEntry["title"], newsEntry["url"], newsEntry["publishedTime"], authorString, newsEntry["summary"], newsEntry["bannerImageURL"], newsEntry["source"], newsEntry["category"], newsEntry["sourceDomain"], newsEntry["overallSentiment"])
                    db.session.add(news)
                    db.session.flush() #retrieving the current article's ID so we can have multiple sentiments for the current articleID in the ArticleTickers table
                    news_id = news.id
                    for sentiment in newsEntry["tickerSentiments"]:
                        if sentiment:
                            sentiments = ArticleTickers(news_id, sentiment["ticker"], sentiment["relevanceScore"], sentiment["sentimentScore"])
                            db.session.add(sentiments)
            db.session.commit()
    


def split_primary_exchanges(json_data):
    new_markets = []
    for market in json_data['markets']:
        exchanges = market['primary_exchanges'].split(', ')
        for exchange in exchanges:
            new_market = market.copy()  # Copy the original market dictionary
            new_market['primary_exchanges'] = exchange  # Replace with the single exchange
            new_markets.append(new_market)
    return new_markets

def fillUpNews():
    for tickerNews in tickers:
        news_item = get_news(tickerNews, '', 'RELEVANCE', 1, '5')
        if news_item:
            for newsEntry in news_item:
                if newsEntry:
                    print(json.dumps(newsEntry, default=custom_serializer, indent=4))
                    authorArr = newsEntry["authors"]
                    authorString = ', '.join(authorArr)
                    news = Articles(newsEntry["tickerID"], newsEntry["title"], newsEntry["url"], newsEntry["publishedTime"], authorString, newsEntry["summary"], newsEntry["bannerImageURL"], newsEntry["source"], newsEntry["category"], newsEntry["sourceDomain"], newsEntry["overallSentiment"])
                    db.session.add(news)
                    db.session.flush() #retrieving the current article's ID so we can have multiple sentiments for the current articleID in the ArticleTickers table
                    news_id = news.id
                    for sentiment in newsEntry["tickerSentiments"]:
                        if sentiment:
                            sentiments = ArticleTickers(news_id, sentiment["ticker"], sentiment["relevanceScore"], sentiment["sentimentScore"])
                            db.session.add(sentiments)
            db.session.commit()








