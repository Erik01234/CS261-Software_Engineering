from sqlalchemy import create_engine, Column, Time
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from sqlalchemy import ForeignKey, Time
import datetime
from datetime import datetime
import pandas as pd

db = SQLAlchemy()

import requests

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

        

        if overview_data["MarketCapitalization"] != None and overview_data["PERatio"] != None and overview_data["EPS"] != None and overview_data["ROE"] != None:
            if overview_data["MarketCapitalization"] != "None" and overview_data["PERatio"] != "None" and overview_data["EPS"] != "None" and overview_data["ROE"] != "None":
                print(overview_data)
                return overview_data
            else:
                return 0
        else:
            return 0
    
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except Exception as err:
        return f"An error occurred: {err}"





companies = pd.read_csv('SP_500.csv')

tickers = companies['Symbol'].unique()




#company_static_info["Symbol"]


class Users(db.Model):
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
    #will fill this up with those 500 companies that we are going to track 
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
    #stores which users are following which company - a simple pairing
    __tablename__ = 'usercompany'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Text())
    company = db.Column(db.Text())

    def __init__(self, user, company):
        self.user = user
        self.company = company


class Articles(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255))
    publishedTime = db.Column(db.DateTime)
    summary = db.Column(db.Text())
    bannerImageURL = db.Column(db.String(255))
    source = db.Column(db.String(255))
    category = db.Column(db.String(255))
    sourceDomain = db.Column(db.String(255))
    overallSentiment = db.Column(db.String(50))

    def __init__(self, url, publishedTime, summary, bannerImageURL, source, category, sourceDomain, overallSentiment):
        self.url = url
        self.publishedTime = publishedTime
        self.summary = summary
        self.bannerImageURL = bannerImageURL
        self.source = source
        self.category = category
        self.sourceDomain = sourceDomain
        self.overallSentiment = overallSentiment

    
class ArticleTickers(db.Model):
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
    __tablename__ = 'topgainers'
    ticker = db.Column(db.String(10), primary_key=True)
    price = db.Column(db.Float(precision=6))
    change = db.Column(db.Float(precision=6))
    changePercent = db.Column(db.Float(precision=6))
    volume = db.Column(db.Float)

    def __init__(self, price, change, changePercent, volume):
        self.price = price
        self.change = change
        self.changePercent = changePercent
        self.volume = volume

class TopLosers(db.Model):
    __tablename__ = 'toplosers'
    ticker = db.Column(db.String(10), primary_key=True)
    price = db.Column(db.Float(precision=6))
    change = db.Column(db.Float(precision=6))
    changePercent = db.Column(db.Float(precision=6))
    volume = db.Column(db.Float)

    def __init__(self, price, change, changePercent, volume):
        self.price = price
        self.change = change
        self.changePercent = changePercent
        self.volume = volume


class ActivelyTraded(db.Model):
    __tablename__ = 'activelytraded'
    ticker = db.Column(db.String(10), primary_key=True)
    price = db.Column(db.Float(precision=6))
    change = db.Column(db.Float(precision=6))
    changePercent = db.Column(db.Float(precision=6))
    volume = db.Column(db.Float)

    def __init__(self, price, change, changePercent, volume):
        self.price = price
        self.change = change
        self.changePercent = changePercent
        self.volume = volume

class GlobalMarket(db.Model):
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


def dbinit():
        #Tasneem - Tasneem
        #Danyal - Danyal
        #Rachel - Rachel
        #Michael - Michael
        #Marios - Marios
    pwderik = generate_password_hash("erikpwd")
    pwdtasneem = generate_password_hash("Tasneem")
    pwddanyal = generate_password_hash("Danyal")
    pwdrachel = generate_password_hash("Rachel")
    pwdmichael = generate_password_hash("Michael")
    pwdmarios = generate_password_hash("Marios")
    pwdadmin = generate_password_hash("admin")
    user_list = [
        Users("rikifekete2003@gmail.com",pwderik,"x",1),
        Users("Tasneem", pwdtasneem, "x", 1),
        Users("Danyal", pwddanyal, "x", 1),
        Users("Rachel", pwdrachel, "x", 1),
        Users("Michael", pwdmichael, "x", 1),
        Users("Marios", pwdmarios, "x", 1),
        Users("admin", pwdadmin, "x", 0),
        #Company(ticker, company_statistic_info["Name"], company_statistic_info["Sector"], company_statistic_info["Industry"], company_statistic_info["Exchange"], company_statistic_info["Currency"], company_statistic_info["Country"], company_statistic_info["Address"], company_statistic_info["Description"])
        ]
    db.session.add_all(user_list)
    db.session.commit()
    for tickerList in tickers:
        company_statistic_info = get_static_company_info(tickerList)
        if company_statistic_info != 0:
            db.session.add(Company(tickerList, company_statistic_info["Name"], company_statistic_info["Sector"], company_statistic_info["Industry"], company_statistic_info["Exchange"], company_statistic_info["Currency"], company_statistic_info["Country"], company_statistic_info["Address"], company_statistic_info["Description"]))
            db.session.commit()

    for tickerOverview in tickers:
        overview = get_company_overview(tickerOverview)
        if overview != 0:
            db.session.add(FinancialData(tickerOverview, datetime.now(), overview["MarketCapitalization"], overview["PERatio"], overview["EPS"], overview["ROE"]))
            db.session.commit()
    
    for tickerStock in tickers:
        stockPriceList = get_current_stock_price_and_volume(tickerStock)
        if stockPriceList != 0:
            db.session.add(CurrentStockPrice(tickerStock, datetime.now(), stockPriceList["Current Price"], stockPriceList["Current Volume"]))
            db.session.commit()
    
    #notes, observations from insertion into DB
        #Company table name doesn't contain the comapny name, but the stock exchange (NYSE or NASDAQ)
        #so Company's name and exchange attribute has the same values!!!

def companyInit():
    for tickerList in tickers:
        company_statistic_info = get_static_company_info(tickerList)
        if company_statistic_info != 0:
            db.session.add(Company(tickerList, company_statistic_info["Name"], company_statistic_info["Sector"], company_statistic_info["Industry"], company_statistic_info["Exchange"], company_statistic_info["Currency"], company_statistic_info["Country"], company_statistic_info["Address"], company_statistic_info["Description"]))
            db.session.commit()
