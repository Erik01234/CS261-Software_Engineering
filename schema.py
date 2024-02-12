from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from sqlalchemy import ForeignKey

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

class TopGainersLosers(db.Model):
    __tablename__ = 'topgainerslosers'
    id = db.Column(db.Integer, primary_key=True)
    tickerID = db.Column(db.Integer, db.ForeignKey('company.ticker'))
    gainerLoserScore = db.Column(db.Float(precision=25))

    def __init__(self, companyID, gainerLoserScore):
        self.companyID = companyID
        self.gainerLoserScore = gainerLoserScore
        #as I see, top gainers and top losers is one list, combining 1) metadata, 2) last updated, 3) top gainers, 4) top losers, 5) most actively traded
        #got to break up the list, arrange them in order (if not in it already) (desc for gainers, asc for losers), and select which of these 5 we need 
        #+ attribute names (i.e., for what values)? What do we store from these? Auxiliary columns (like 1 for gainer, 0 for loser)?


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