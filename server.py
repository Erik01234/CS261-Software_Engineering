import os
from flask import Flask, request, redirect, render_template, url_for, session, send_from_directory, jsonify
app = Flask(__name__, static_url_path="/static")
app.secret_key = 'incredibly secret key of ours'
from datetime import datetime, timedelta, date
from werkzeug import security
from markupsafe import escape
from sqlalchemy import and_, or_, not_, func, desc, asc, distinct
from flask_mail import Mail, Message
import re #for the signup page
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import yagmail 
from schema import db, dbinit, Users, get_current_stock_price_and_volume, CurrentStockPrice, get_company_overview, FinancialData, getTopGainersLosers, TopGainers, TopLosers, ActivelyTraded, split_primary_exchanges, get_global_market, GlobalMarket, fillUpNews, Articles, ArticleTickers, UserCompany, SavedArticles, Company
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
srializer = URLSafeTimedSerializer('xyz567')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24) 
import pandas as pd
import signal
import sys
import json
#session is going to terminate after 30 minutes
mail = Mail(app)
db.init_app(app)



resetwholedb = False
if resetwholedb:
    with app.app_context():
        db.drop_all()
        db.create_all()
        dbinit()



with open('smtp_credentials.txt', 'r') as file:
    app_pwd = file.read() 
    #app specific password, not my actual gmail password

gmail_user = "rikifekete2003@gmail.com"
gmail_password = app_pwd 
yag = yagmail.SMTP(gmail_user, gmail_password, host="smtp.gmail.com")


companies = pd.read_csv('SP_500.csv')
tickers = companies['Symbol'].unique()


def dailyUpdates():

    #for ticker in tickers:     WAS REMOVED, CAUSED ERRORS WITH THE TG TL MAT tables, coz it was iterating through all 500 and fetching data - takes no parameters though
    with app.app_context():
        #example on updating the DB instead of dropping and inserting
        '''currentCurrent = CurrentStockPrice.query.filter_by(tickerID=ticker).first()
            if currentCurrent and currentCurrent.tickerID:
            stockPriceList = get_current_stock_price_and_volume(ticker)
            currentCurrent.timestamp = datetime.now()
            currentCurrent.stockPrice = stockPriceList["Current Price"]
            currentCurrent.volumeOfTrade = stockPriceList["Current Volume"]
            db.session.commit()'''
        
        today = date.today()
        today_articles = Articles.query.filter(func.date(Articles.publishedTime) == today).all()
        # Count occurrences of tickers
        ticker_count = {}
        for article in today_articles:
            ticker = article.tickerID
            if ticker in ticker_count:
                ticker_count[ticker] += 1
            else:
                ticker_count[ticker] = 1
        most_common_ticker = max(ticker_count, key=ticker_count.get)
        print(most_common_ticker+" IS THE MOST WRITTEN COMPANY")

        bearish_count = {}
        for article in today_articles:
            ticker = article.tickerID
            sentiment = article.overallSentiment
            if sentiment == "Somewhat-Bearish":
                if ticker in bearish_count:
                    bearish_count[ticker] += 1
                else:
                    bearish_count[ticker] = 1
        
        most_bearish_ticker = max(bearish_count, key=bearish_count.get)
        print(most_bearish_ticker+" IS THE MOST BEARISH COMPANY")

        bullish_count = {}
        for article in today_articles:
            ticker = article.tickerID
            sentiment = article.overallSentiment
            if sentiment == "Bullish":
                if ticker in bullish_count:
                    bullish_count[ticker] += 1
                else:
                    bullish_count[ticker] = 1
        
        most_bullish_ticker = max(bullish_count, key=bullish_count.get)
        print(most_bullish_ticker+" IS THE MOST BULLISH COMPANY")


        userIDsQuery = Users.query.all() 
        #first get all Users
        for user in userIDsQuery:
            #iterate through the rows (users)
            userid = user.id
            usernm = user.email
            print(str(usernm))
            print(usernm)
            #grab the user's ID
            followed_companies = [uc.company for uc in UserCompany.query.filter(UserCompany.user == userid)]
            #get a followed companies list
            userArticles = []
            for company in followed_companies:
                bullish_articles = Articles.query.filter(Articles.tickerID == company, Articles.overallSentiment == "Bullish").order_by(desc(Articles.publishedTime)).limit(5).all()
                if len(bullish_articles) > 0:
                    userArticles.extend(bullish_articles)
                bearish_articles = Articles.query.filter(Articles.tickerID == company, or_(Articles.overallSentiment == "Bearish", Articles.overallSentiment == "Somewhat-Bearish")).order_by(desc(Articles.publishedTime)).limit(5).all()
                if len(bearish_articles) > 0:
                    userArticles.extend(bearish_articles)
            user_articles_data = [{"headline": article.title, "url": article.url} for article in userArticles]
            print(user_articles_data)

            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
            def check(usernm):
                if(re.fullmatch(regex, str(usernm))):
                    return True
                else:
                    return False
            check(user)
            if check(usernm):
                if not user_articles_data:
                    msgbody = f"""
                    <h1>Hello {usernm}! Your Daily Updates Are Here:</h1>
                    <h2>Global Stats</h2>
                    <ul>
                    <li>Most written company: {most_common_ticker}</li>
                    <li>Most bullish company: {most_bullish_ticker}</li>
                    <li>Most bearish company: {most_bearish_ticker}</li>
                    </ul>
                    <p>Regards, <a href="localhost:3000">CoRNIA</a></p>
                    """
                    message = f"Subject: Updates\n\n{msgbody}"
                    yag.send(to=usernm, contents=[message])
                else:
                    msgbody = f"""
                    <html>
                        <body>
                            <h1>Hello There! Your Daily Updates Are Here:</h1>
                            <h2>Here are some articles for you:</h2>
                            {''.join([
                                f'<div class="article"><div class="headline"><a href="{article["url"]}">{article["headline"]}</a></div></div>'
                                for article in user_articles_data
                            ])}
                            <h2>Global Stats</h2>
                            <ul>
                                <li>Most written company: {most_common_ticker}</li>
                                <li>Most bullish company: {most_bullish_ticker}</li>
                                <li>Most bearish company: {most_bearish_ticker}</li>
                            </ul>
                            <p>Regards, <a href="localhost:3000">CoRNIA</a></p>
                        </body>
                    </html>
                    """
                    message = f"Subject: Updates\n\n{msgbody}"
                    yag.send(to=usernm, contents=[message])


def frequentUpdates(): 
    with app.app_context():
        #UNCOMMENT AFTER TESTING:
        db.metadata.drop_all(bind=db.engine, tables=[TopGainers.__table__])
        db.metadata.create_all(bind=db.engine, tables=[TopGainers.__table__])
        db.metadata.drop_all(bind=db.engine, tables=[TopLosers.__table__])
        db.metadata.create_all(bind=db.engine, tables=[TopLosers.__table__])
        db.metadata.drop_all(bind=db.engine, tables=[ActivelyTraded.__table__])
        db.metadata.create_all(bind=db.engine, tables=[ActivelyTraded.__table__])
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
    
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(frequentUpdates, 'interval', minutes=5)
scheduler.add_job(dailyUpdates, 'interval', hours=24)


def custom_sanitizer(input_from_html):
    chars_to_sanitize = re.compile(r'<[^>]*>')
    sql_operators = ['SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'UNION', 'LIMIT']
    sql_symbols = ['=', '<', '>', '!', ';', "'", '"', '--', '/*', '*/', '&&', '||']
    combined_pattern = '|'.join([chars_to_sanitize.pattern] + [re.escape(op) for op in sql_operators] + [re.escape(sym) for sym in sql_symbols])
    sanitized_html = re.sub(combined_pattern, '', input_from_html)
    return sanitized_html

@app.route('/checkLoggedIn')
def check_logged_in():
    if 'username' in session:
        return jsonify({'loggedIn': True})
    else:
        return jsonify({'loggedIn': False})

@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

@app.route('/saveArticle', methods=["POST"])
def saveArticle():
    try:
        data = request.json
        articleID = data.get('id')
        user = session["username"]
        userIDQuery = Users.query.filter_by(email=user).first()
        userIDQuery = userIDQuery.id
        print(str(articleID))
        toInsert = [
            SavedArticles(userIDQuery, articleID)
        ]
        db.session.add_all(toInsert)
        db.session.commit()

        return jsonify({'message': 'Article saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/follow', methods=["POST"])
def follow():
    try:
        data = request.json
        companyID = data.get('companyId')
        user = session["username"]
        userIDQuery = Users.query.filter_by(email=user).first()
        userIDQuery = userIDQuery.id
        capitalTicker = companyID.upper()
        toInsert = [
            UserCompany(userIDQuery, capitalTicker)
        ]
        db.session.add_all(toInsert)
        db.session.commit()

        return jsonify({'message': 'accept'})
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    

@app.route('/unfollow', methods=["POST"])
def unfollow():
    try:
        data = request.json
        companyID = data.get('companyId')
        user = session["username"]
        userIDQuery = Users.query.filter_by(email=user).first()
        userIDQuery = userIDQuery.id

        capitalTicker = companyID.upper()
        UserCompany.query.filter_by(user=userIDQuery, company=capitalTicker).delete()
        db.session.commit()
        print("here")
        return jsonify({'message': 'accept'})
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    


@app.route('/fetchFilterSector')
def fetchSector():
    try:
        sectors_query = Company.query.with_entities(Company.sector).distinct().order_by(asc(Company.sector)).all()
        sectors_list = [sector[0] for sector in sectors_query]
        print(sectors_list)
        return jsonify(sectors_list)
    except Exception as e:
        return jsonify(error=str(e)), 500
    

@app.route('/fetchFilterCategory')
def fetchCategory():
    try:
        category_query = Articles.query.with_entities(Articles.category).distinct().order_by(asc(Articles.category)).all()
        newlist = []
        for elem in category_query:
            if elem.category == "n/a" and elem not in newlist:
                newlist.append("Misc")
            elif elem.category != "GoogleRSS" and elem.category != "BusinessGoogleRSS":
                if elem not in newlist:
                    newlist.append(elem.category)
        return jsonify(newlist)
    except Exception as e:
        return jsonify(error=str(e)), 500
    


@app.route('/sendTrueValues', methods=["POST"])
def sendTrueValues():
    data = request.json
    true_values = data.get('trueValues', [])
    category = [
    "Business",
    "Companies",
    "Earnings",
    "Economy",
    "Markets",
    "News",
    "Top News",
    "Top Stories",
    "Trading",
    "General",
    "n/a",
    ]
    sector = [
        "ENERGY & TRANSPORTATION",
        "FINANCE",
        "LIFE SCIENCES",
        "MANUFACTURING",
        "REAL ESTATE & CONSTRUCTION",
        "TECHNOLOGY",
        "TRADE & SERVICES"
    ]
    sectorlist = []
    categorylist = []
    publishDate = 0 #0 was asc, 1 was desc
    for item in true_values:
        key = item.get('key')
        index = item.get('index')
        if key == "category":
            if category[index] == "General":
                categorylist.append("n/a")
                categorylist.append("GoogleRSS")
                categorylist.append("BusinessGoogleRSS")
            categorylist.append(category[index])
            
        elif key == "sector":
            sectorlist.append(sector[index])
        elif key == "publishDate":
            publishDate = index
    for elem2 in categorylist:
        print(elem2)
    for elem in sectorlist:
        print(elem)
    print(publishDate)
    
    sectorQuery = Company.query.filter(Company.sector.in_(sectorlist)).all()
    tickerIDForSector = [comp.ticker for comp in sectorQuery]
    #for elem2 in tickerIDForSector:
        #print(elem2)
    sectorQueryArticles = Articles.query.filter(and_(Articles.tickerID.in_(tickerIDForSector), Articles.category.in_(categorylist))).all()

    counter = 0
    for elem in sectorQueryArticles:
        counter = counter + 1
    print(counter)

    

    return jsonify(message="True values received successfully"), 200


    

@app.route('/unsaveArticle', methods=["POST"])
def unsaveArticle():
    try:
        data = request.json
        id = data.get('headline')
        print(id)
        user = session["username"]
        userIDQuery = Users.query.filter_by(email=user).first()
        userIDQuery = userIDQuery.id
        articleIDQuery = Articles.query.filter_by(id=id).first()
        articleID = articleIDQuery.id
        print(userIDQuery)
        print(articleID)
        SavedArticles.query.filter_by(userID=userIDQuery, articleID=articleID).delete()
        db.session.commit()

        return jsonify({'message': 'success'})
    except Exception as e:
        print(e)
        return jsonify({'message': str(e)}), 500
        
    


@app.route('/returnSavedArticles')
def returnSavedArticles():
    user = session["username"]
    userIDQuery = Users.query.filter_by(email=user).first()
    userIDQuery = userIDQuery.id
    savedArticlesQuery = SavedArticles.query.filter_by(userID=userIDQuery).all()
    newsIDsFollowed = [ns.articleID for ns in savedArticlesQuery]   
    news_query = Articles.query.filter(Articles.id.in_(newsIDsFollowed)).all() 
    feed_entries_json = [
        {"headline": entry.title,
        "source": entry.source,
        "time": entry.publishedTime,
        "icon": entry.bannerImageURL,
        "logo": entry.bannerImageURL,
        "company": entry.tickerID,
        "summary": entry.summary,
        "sentiment": entry.overallSentiment,
        "url": entry.url,
        "id": entry.id
        }
        for entry in news_query
    ]
    return jsonify(feed_entries_json)


@app.route('/Homepage')
def homepage():
    user = session["username"]
    userIDQuery = Users.query.filter_by(email=user).first()
    userIDQuery = userIDQuery.id
    usercompanyquery = UserCompany.query.filter_by(user=userIDQuery).all()
    company_tickers_followed = [uc.company for uc in usercompanyquery]
    news_query = Articles.query.filter(Articles.tickerID.in_(company_tickers_followed)).order_by(desc(Articles.publishedTime)).all()
    #news_query = Articles.query.all()
    feed_entries_json = [
        {"headline": entry.title,
        "source": entry.source,
        "time": entry.publishedTime,
        "icon": entry.bannerImageURL,
        "logo": entry.bannerImageURL,
        "company": entry.tickerID,
        "url": entry.url,
        'id': entry.id,
        'summary': entry.summary,
        'sentiment': entry.overallSentiment
        }
        for entry in news_query
    ]
    return jsonify(feed_entries_json)

@app.route("/checkFollowStatus", methods=["POST"])
def check_follow_status():
    data = request.json
    companyId = data.get("companyId")
    user = session["username"]
    userIDQuery = Users.query.filter_by(email=user).first()
    userId = userIDQuery.id
    companyId = companyId.upper()
    recordCount = UserCompany.query.filter_by(user=userId, company=companyId).first() 
    if recordCount is not None:
        is_followed = True
    else:
        is_followed = False
    #print(companyId+" followed: "+str(is_followed))
    return jsonify({"isFollowed": is_followed})


@app.route('/updateCompany', methods=["POST"])
def updateCompany():
    data = request.json
    companyId = data.get("companyId")
    user = session["username"]
    userIDQuery = Users.query.filter_by(email=user).first()
    userId = userIDQuery.id
    companyId = companyId.upper()
    data1 = get_company_overview(companyId)
    data2 = get_current_stock_price_and_volume(companyId)
    timestamp = datetime.now()
    if data1:
        if data2:
            stockQuery = CurrentStockPrice.query.filter_by(tickerID=companyId).first()
            stockQuery.stockPrice = data2["Current Price"]
            stockQuery.volumeOfTrade = data2["Current Volume"]
            stockQuery.timestamp = timestamp

            financialQuery = FinancialData.query.filter_by(tickerID=companyId).first()
            if data1["MarketCapitalization"] != "None":
                financialQuery.marketCap = data1["MarketCapitalization"]
            else:
                financialQuery.marketCap = 0
            if data1["PERatio"] != "None":
                financialQuery.pe_ratio = data1["PERatio"]
            else:
                financialQuery.pe_ratio = 0
            if data1["EPS"] != "None":
                financialQuery.eps = data1["EPS"]
            else:
                financialQuery.eps = 0
            if data1["ROE"] != "None":
                financialQuery.roe = data1["ROE"]
            else:
                financialQuery.roe = 0

            db.session.commit()

    return jsonify({"message": "success"})

   

@app.route('/similarCompany', methods=["POST"])
def similarCompany():
    data = request.json
    companyId = data.get("companyId")
    companyId = companyId.upper()
    print(str(companyId)+" is the company ID")
    user = session["username"]
    userIDQuery = Users.query.filter_by(email=user).first()
    userId = userIDQuery.id
    companyQuery = Company.query.filter_by(ticker=companyId).first()
    sector = companyQuery.sector
    industry = companyQuery.industry
    similarQuery = Company.query.filter(Company.industry==industry, Company.sector==sector, not_(Company.ticker == companyId)).limit(5).all()
    #print(str(len(similarQuery))+" IS OUR COUNT")
    if len(similarQuery) < 5:
        #less than 5
        additional_companies = Company.query.filter(Company.sector == sector, not_(Company.industry == industry)).limit(5-len(similarQuery)).all()
        similarQuery.extend(additional_companies)
        if len(similarQuery) < 5:
            more_query = Company.query.filter(not_(Company.sector == sector), Company.industry == industry).limit(5-len(similarQuery)).all()
            similarQuery.extend(more_query)
    #company_names = [uc.name for uc in similarQuery]
    names = [
        {"name": entry.name,
         'ticker': entry.ticker
        }
        for entry in similarQuery
    ]
    
    return (jsonify(names))


@app.route('/relatedNews', methods=["POST"])
def relatedNews():
    data = request.json
    companyId = data.get("companyId")
    companyId = companyId.upper()
    print(str(companyId)+" is the company ID")
    user = session["username"]
    userIDQuery = Users.query.filter_by(email=user).first()
    userId = userIDQuery.id
    relatedQuery = Articles.query.filter(Articles.tickerID==companyId).order_by(desc(Articles.publishedTime)).limit(3).all()
    names = [
        {"headline": entry.title[:100] + "..." if len(entry.title) > 100 else entry.title,
         "source": entry.url,
         "icon": entry.bannerImageURL,
         "summary": entry.summary,
         "id": entry.id
        }
        for entry in relatedQuery
    ]
    
    return (jsonify(names))



@app.route('/searchCompany', methods=["POST"])
def searchCompany():
    data = request.json
    stringd = data.get("string")
    string = stringd.lower()
    string = custom_sanitizer(string)
    print(string+" IS OUR STRING")
    #print(string+" IS OUR STRIIIING")
    companyname_starts_with = Company.query.filter(or_(func.lower(Company.name).startswith(string), func.lower(Company.ticker).contains(string))).limit(5).all()
    companies = companyname_starts_with
    ''' This causes duplicates:
    companyname_starts_with = Company.query.filter(func.lower(Company.name).startswith(string)).limit(5).all()
    companies_contains = Company.query.filter(or_(func.lower(Company.ticker).contains(string), func.lower(Company.name).contains(string))).limit(5).all()
    companies = companyname_starts_with + companies_contains
    '''
    if len(companies) == 0:
        return (jsonify({"message": "empty"}))
    for elem in companies:
        print(elem.name+" IS A COMPANY")
    companyList = [
        {"name": entry.name,
         "ticker": entry.ticker,
         "sector": entry.sector,
         "industry": entry.industry
        }
        for entry in companies
    ]
    return (jsonify(companyList))

@app.route('/searchHeadline', methods=["POST"])
def searchHeadline():
    data = request.json
    stringd = data.get("string")
    string = stringd.lower()
    string = custom_sanitizer(string)
    articles = Articles.query.filter(func.lower(Articles.title).contains(string)).order_by(desc(Articles.publishedTime)).limit(15).all()
    if len(articles) == 0:
        return (jsonify({"message": "empty"}))
    for elem in articles:
        print(elem.title+" IS A TITLE")
        print(str(elem.id)+" IS THE CORRESPONDING ID")
    articleList = [
        {"id": entry.id,
         "ticker": entry.tickerID,
         "title": entry.title,
         "url": entry.url,
         "source": entry.source,
         "summary": entry.summary,
         "image": entry.bannerImageURL,
         "sentiment": entry.overallSentiment,
         "time": entry.publishedTime
        }
        for entry in articles
    ]
    return (jsonify(articleList))






@app.route("/checkSaveStatus", methods=["POST"])
def check_save_status():
    data = request.json
    articleId = data.get("articleID")
    user = session["username"]
    userIDQuery = Users.query.filter_by(email=user).first()
    userId = userIDQuery.id
    recordCount = SavedArticles.query.filter_by(userID=userId, articleID=articleId).first() 
    if recordCount is not None:
        is_saved = True
    else:
        is_saved = False
    return jsonify({"isFollowed": is_saved})




@app.route('/followedCompanies')
def followedCompanies():
    user = session["username"]
    userIDQuery = Users.query.filter_by(email=user).first()
    userIDQuery = userIDQuery.id
    usercompanyquery = UserCompany.query.filter_by(user=userIDQuery).all()
    company_ticker_query = [uc.company for uc in usercompanyquery]
    company_query = Company.query.filter(Company.ticker.in_(company_ticker_query)).all()
    print("Length of query is "+str(len(company_query)))
    company_entries_json = [
        {"companyName": entry.name,
         "companyTicker": entry.ticker,
         "sector": entry.sector,
         "industry": entry.industry
        }
        for entry in company_query
    ]
    return jsonify(company_entries_json)

@app.route('/Discover')
def discover():
    num_articles = request.args.get('limit', type=int) or 10
    offset = request.args.get('offset', type=int) or 0
    news_query = Articles.query.order_by(desc(Articles.publishedTime)).limit(num_articles).offset(offset).all()
    #news_query = Articles.query.all()
    merged_entries = {}
    #print("MERGED ENTRIES SESSION CONTAINS: "+str(merged_entries))

    '''
    session method could theoretically work BUT:
        how does it merge About Company buttons for a headline corresponding to multiple companies (tickers) if, for one, 
        offset is 0 (loaded initially), and for the other, offset is, say, 10? If session implementation is correct, it won't just "add"
        the company name ALSO corresponding to a previously shown article to that article, but rather will just ignore it

    THIS RIGHT HERE is the current possible best implementation within the time frame, other requirements and 
    the unimportance of perfecting this already good implementation
    '''
    
    for entry in news_query:
        article_key = (entry.title)
        if article_key in merged_entries or entry.id in merged_entries:
            # If the article key exists, append the ticker
            merged_entries[article_key]['company'].append(entry.tickerID)
            #count = 0
            #for elem in merged_entries[article_key]['company']:
                #count = count+1
                #print(str(count)+"th ELEM IS "+elem)
            #count = 0
        else:
            logopath = "cornialogo.png"
            if entry.bannerImageURL is not None or entry.bannerImageURL == "":
                merged_entries[article_key] = {
                    "headline": entry.title,
                    "source": entry.source,
                    "time": entry.publishedTime,
                    "icon": entry.bannerImageURL,
                    "logo": entry.bannerImageURL,
                    "company": [entry.tickerID],
                    "id": entry.id,
                    'summary': entry.summary,
                    'sentiment': entry.overallSentiment,
                    "url": entry.url
                }
            else:
                print("IMAGE FOR ENTRY ID: "+str(entry.id)+" IS NONEXISTENT. PLACING UNIQUE IMAGE")
                merged_entries[article_key] = {
                    "headline": entry.title,
                    "source": entry.source,
                    "time": entry.publishedTime,
                    "icon": "https://cdn.pixabay.com/photo/2013/07/12/19/16/newspaper-154444_960_720.png",
                    "logo": "https://cdn.pixabay.com/photo/2013/07/12/19/16/newspaper-154444_960_720.png",
                    "company": [entry.tickerID],
                    "id": entry.id,
                    'summary': entry.summary,
                    'sentiment': entry.overallSentiment,
                    "url": entry.url
                }
    #print("MERGED ENTRIES AFTER OFFSET "+str(offset)+" IS "+str(merged_entries))
    feed_entries_json = list(merged_entries.values())
    return jsonify(feed_entries_json)


@app.route('/fetchgainer')
def fetchgainer():
    gainers_query = TopGainers.query.limit(5).all()
    #news_query = Articles.query.all()
    feed_entries_json = [
        {"company": entry.ticker,
        "value": round(entry.changePercent, 2),
        }
        for entry in gainers_query
    ]
    print("something")
    for elem in feed_entries_json:
        print(str(elem))
    return jsonify(feed_entries_json)

@app.route('/fetchloser')
def fetchloser():
    losers_query = TopLosers.query.limit(5).all()
    #news_query = Articles.query.all()
    feed_entries_json = [
        {"company": entry.ticker,
        "value": round(entry.changePercent, 2),
        }
        for entry in losers_query
    ]
    return jsonify(feed_entries_json)

@app.route('/fetchmostactive')
def fetchmostactive():
    active_query = ActivelyTraded.query.limit(5).all()
    #news_query = Articles.query.all()
    feed_entries_json = [
        {"company": entry.ticker,
        "value": round(entry.volume, 2),
        }
        for entry in active_query
    ]
    return jsonify(feed_entries_json)



@app.route('/retrieveCompany', methods=["POST"])
def retrieveCompany():
    data = request.json
    ticker = data.get('companyId')
    capitalTicker = ticker.upper()
    print(capitalTicker)
    companyQuery = Company.query.filter_by(ticker=capitalTicker).first()
    stockQuery = CurrentStockPrice.query.filter_by(tickerID=capitalTicker).first()
    financialQuery = FinancialData.query.filter_by(tickerID=capitalTicker).first()
    roundStock = round(stockQuery.stockPrice, 2)
    roundVolume = round(stockQuery.volumeOfTrade, 2)
    roundCap = round(financialQuery.marketCap, 2)
    roundPe = round(financialQuery.pe_ratio, 2)
    roundEps = round(financialQuery.eps, 2)
    roundRoe = round(financialQuery.roe, 2)

    companyData = [{
        "name": companyQuery.name,
        "ticker": companyQuery.ticker,
        "sector": companyQuery.sector,
        "industry": companyQuery.industry,
        "exchange": companyQuery.exchange,
        "currency": companyQuery.currency,
        "address": companyQuery.address,
        "description": companyQuery.description,
        "timestamp": stockQuery.timestamp,
        "stockprice": roundStock, 
        "volume": roundVolume,
        "marketcap": roundCap,
        "pe": roundPe,
        "eps": roundEps,
        "roe": roundRoe,
        "trend": companyQuery.projection
    }]
    return jsonify(companyData)


@app.route('/submitlogin', methods=['POST', 'GET'])
def login():
    
    '''if request.method == 'POST':
        email = request.form.get("email")
        email = escape(email)
        passwd = request.form.get("password")
        passwd = escape(passwd)
        session["username"] = email
        users = Users.query.filter_by(email=email).first()
        if users == None:
            
            try:
              del session['username']
            except KeyError:
                pass
            session.pop('username', None)
            session.clear()

            return "Incorrect email. Try again!"
        useractivated = users.isactivated
        if not security.check_password_hash(users.hashed_password, passwd): 
            try:
              del session['username']
            except KeyError:
                pass
            session.pop('username', None)
            session.clear()
            return "Incorrect password. Try again!"
        else:
            if useractivated == 0:
              token = srializer.dumps(email, salt='email-confirm')
              link = url_for('confirmemail', token=token, external=True)
              urlbeginning = request.base_url
              urlnew = urlbeginning+link
              urlnew = urlnew.replace("/submitlogin", "")
              #print("URL to receive by person signing up is: "+urlnew)
              msgbody = 'Your new verification link is {}'.format(urlnew)
              message = f"Subject: Email verification\n\n{msgbody}"
              yag.send(to=email, contents=[message])
              users.temptoken = token
              db.session.commit()

              try:
                del session['username']
              except KeyError:
                pass
              session.pop('username', None)
              session.clear()
              return '<p>Your account is not activated. Another email was sent to you to verify your address</p><br /><p>The email you entered is {}<br /><p>Activate your account in an hour. If you cant, you can receive a new confirmation email on a login attempt</p><br /><form action="/login"><input type="submit" value="Return"></form>'.format(email)
            elif useractivated == 1:
              return redirect('/')'''
    data = request.json
    email = data.get('username')
    passwd = data.get('password')
    email = custom_sanitizer(email)
    passwd = custom_sanitizer(passwd)
    users = Users.query.filter_by(email=email).first()
    useractivated = users.isactivated
    if users == None:
        response_message = 'deny'
    if not security.check_password_hash(users.hashed_password, passwd): 
        response_message = 'deny'
    else:
        if useractivated == 0:
            '''token = srializer.dumps(email, salt='email-confirm')
            link = url_for('confirmemail', token=token, external=True)
            urlbeginning = request.base_url
            urlnew = urlbeginning+link
            urlnew = urlnew.replace("/submitlogin", "")
            #print("URL to receive by person signing up is: "+urlnew)
            msgbody = 'Your new verification link is {}'.format(urlnew)
            message = f"Subject: Email verification\n\n{msgbody}"
            yag.send(to=email, contents=[message])
            users.temptoken = token
            db.session.commit()'''
            response_message = 'deny'
        else:
            response_message = 'accept'
            session['username'] = email
            
    return jsonify({'message': response_message})
    

@app.route('/logout')
def logout():
    try:
        del session['username']
    except KeyError:
        pass
    session.pop('username', None)
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200


@app.route('/submitsignup', methods=['POST', 'GET'])
def submitsignup():
    

    
    '''usernm = request.form.get("email")
    usernm = escape(usernm)
    passwd = request.form.get("password")
    passwd = escape(passwd)
    hashed_pwd = generate_password_hash(passwd)
    passwordre = request.form.get("repeated")
    passwordre = escape(passwordre)
    token = srializer.dumps(usernm, salt='email-confirm')
    users = Users.query.filter_by(email=usernm).first()

    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    def check(usernm):
        if(re.fullmatch(regex, usernm)):
            return True
        else:
            return False
    
    check(usernm)

    if request.method == 'POST':
        if check(usernm):
            if users == None:
                if passwd == passwordre:
                    all_users = [
                        Users(usernm,hashed_pwd,token, 0), 
                    ]
                    db.session.add_all(all_users)
                    db.session.commit()
                    link = url_for('confirmemail', token=token, external=True)
                    urlbeginning = request.base_url
                    urlnew = urlbeginning+link
                    urlnew = urlnew.replace("/submitsignup", "")
                    #print("URL to receive by person signing up is: "+urlnew)
                    msgbody = 'Your verification link is {}'.format(urlnew)
                    message = f"Subject: Email verification\n\n{msgbody}"
                    yag.send(to=usernm, contents=[message])

                    return '<div align="center"><p>The email you entered is {}. </p><p>Activate your account in an hour. If you cant, you can receive a new confirmation email on a login attempt.</p><form action="/login"><input type="submit" value="Return"></form></div>'.format(usernm)
                else:
                    return "Passwords should match. Try again!"
            else:
                return "User already exists! Please choose a different username!"
        else:
            return "Invalid email format. Try again!"'''
        


    data = request.json
    usernm = data.get('email')
    usernm = custom_sanitizer(usernm)
    passwd = data.get('password')
    hashed_pwd = generate_password_hash(passwd)
    passwordre = data.get('confirmPassword')
    passwordre = custom_sanitizer(passwordre)
    token = srializer.dumps(usernm, salt='email-confirm')
    
    users = Users.query.filter_by(email=usernm).first()

    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    def check(usernm):
        if(re.fullmatch(regex, usernm)):
            return True
        else:
            return False
    
    check(usernm)

    if check(usernm):
            if users == None:
                if passwd == passwordre:
                    all_users = [
                        Users(usernm,hashed_pwd,token, 1), 
                    ]
                    db.session.add_all(all_users)
                    db.session.commit()
                    '''link = url_for('confirmemail', token=token, external=True)
                    urlbeginning = request.base_url
                    urlnew = urlbeginning+link
                    urlnew = urlnew.replace("/submitsignup", "")
                    #print("URL to receive by person signing up is: "+urlnew)
                    msgbody = 'Your verification link is {}'.format(urlnew)
                    message = f"Subject: Email verification\n\n{msgbody}"
                    yag.send(to=usernm, contents=[message])'''
                    response_message = 'accept'
                else:
                    response_message = 'deny'
            else:
                response_message = 'deny'
    else:
        response_message = 'deny'
            
    return jsonify({'message': response_message})



@app.route('/confirmemail/<token>')
def confirmemail(token):
  email = srializer.loads(token, salt='email-confirm', max_age=3600)
  users = Users.query.filter_by(email=email).first()
  users.isactivated = 1
  db.session.commit()
  return '<p>Yay, {}, you have just activated your email!</p><form action="/"><input type="submit" value="Return to login"></form>'.format(email)