from sqlalchemy import create_engine, Column, Time
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from sqlalchemy import ForeignKey, Time
import datetime

db = SQLAlchemy()

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
    ticker = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    sector = db.Column(db.Text())
    assetType = db.Column(db.String)
    exchange = db.Column(db.String)
    currency = db.Column(db.String)
    country = db.Column(db.String)
    address = db.Column(db.Text())

    def __init__(self, name, sector, assetType, exchange, currency, country, address):
        self.name = name
        self.sector = sector
        self.assetType = assetType
        self.exchange = exchange
        self.currency = currency
        self.country = country
        self.address = address

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
        Users("admin", pwdadmin, "x", 0) #testing purposes
        ]
    db.session.add_all(user_list)
    db.session.commit()