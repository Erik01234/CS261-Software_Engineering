import os
from flask import Flask, request, redirect, render_template, url_for, session, send_from_directory, jsonify
from datetime import datetime, timedelta, date
from werkzeug import security
from markupsafe import escape
from sqlalchemy import and_, or_, not_, func, desc, asc, distinct, extract
from flask_mail import Mail, Message
import re #for the signup page
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import yagmail 
from schema import db, dbinit, Users, get_current_stock_price_and_volume, CurrentStockPrice, get_company_overview, FinancialData, getTopGainersLosers, TopGainers, TopLosers, ActivelyTraded, split_primary_exchanges, get_global_market, GlobalMarket, fillUpNews, Articles, ArticleTickers, UserCompany, SavedArticles, Company
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import pandas as pd
import requests
import signal
import sys
import json
#we do the required imports for this flask backend above

app = Flask(__name__, static_url_path="/static")
app.secret_key = 'incredibly secret key of ours'
srializer = URLSafeTimedSerializer('xyz567')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30) 
mail = Mail(app)
db.init_app(app)
#we also initialize the app, a secret key for the password hashes, the database, 
#the mail service, and the session lifetime for extra security (set to 30 minutes)

resetwholedb = False
if resetwholedb:
    with app.app_context():
        db.drop_all()
        db.create_all()
        dbinit()
#this function is only called if resetwholedb is True - only set to True for debugging, 
#as it drops the table, creates all, and fills up with initial data



with open('smtp_credentials.txt', 'r') as file:
    app_pwd = file.read() 
    #imports my app specific gmail password from an external (gitignored) file

gmail_user = "rikifekete2003@gmail.com"
gmail_password = app_pwd 
yag = yagmail.SMTP(gmail_user, gmail_password, host="smtp.gmail.com")
#setting up the mail service with my email and password


companies = pd.read_csv('SP_500.csv')
tickers = companies['Symbol'].unique()
#read the companies from a static CSV file for S&P 500
#get a list of unique tickers utilised later


def format_news_feed_data(data):
    #function called for formatting the regularly fetched news articles, + initialize empty list to later return
    articles = []
    for item in data.get('feed', []):
        try:
            publishedTime = datetime.strptime(item.get('time_published'), "%Y%m%dT%H%M%S")
            #convert published time into proper format
        except ValueError:
            publishedTime = 'N/A'  #handle incorrect format gracefully
        
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
            #format ticker_sentiment just like we did in schema, and for each ticker sentiment, append the formatted version it into the list
        
            article = {
                "tickerID": ticker_detail.get('ticker', 'N/A'), 
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
            #format news as well, BUT for each ticker corresponding to an article's ticker sentiment, create a new record
            #this is due to us handling redundancy and repetition on query, not insertion
            #thus to stay consistent, we insert this way
    return articles
    #return to the scheduler function


#this function handles one part of the daily updates, including the mailing system described and shown in the demo video
#retrieves both general as well as personalised data for the user to be mailed
def dailyUpdates():

    with app.app_context():
        
        #we start with the GENERAL stats
        today = date.today()
        today_articles = Articles.query.filter(func.date(Articles.publishedTime) == today).all()
        #get today's articles
        ticker_count = {}
        for article in today_articles:
            ticker = article.tickerID
            if ticker in ticker_count:
                ticker_count[ticker] += 1
            else:
                ticker_count[ticker] = 1
        #Count occurrences of tickers
        most_common_ticker = max(ticker_count, key=ticker_count.get)
        #get the ticker that is most written about, as for today
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
        #count occurrences of tickers with bearish news
        
        most_bearish_ticker = max(bearish_count, key=bearish_count.get)
        #get the ticker with the most bearish news
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
        #count occurrences of tickers with bullish news
        most_bullish_ticker = max(bullish_count, key=bullish_count.get)
        #get the ticker with the most bullish news
        print(most_bullish_ticker+" IS THE MOST BULLISH COMPANY")


        #now for the PERSONALISED stats in the email
        userIDsQuery = Users.query.all() 
        #first get all Users
        for user in userIDsQuery:
            #iterate through the rows (users!)
            userid = user.id
            usernm = user.email
            print(str(usernm))
            print(usernm)
            #grab the user's ID
            followed_companies = [uc.company for uc in UserCompany.query.filter(UserCompany.user == userid)]
            #get a list of followed companies for the user
            userArticles = []
            for company in followed_companies:
                #iterate through the followed companies for the current user
                bullish_articles = Articles.query.filter(Articles.tickerID == company, Articles.overallSentiment == "Bullish").order_by(desc(Articles.publishedTime)).limit(5).all()
                #get max 5 bullish articles corresponding to the current company
                if len(bullish_articles) > 0:
                    userArticles.extend(bullish_articles)
                    #if any exist, extend the initially empty list
                bearish_articles = Articles.query.filter(Articles.tickerID == company, or_(Articles.overallSentiment == "Bearish", Articles.overallSentiment == "Somewhat-Bearish")).order_by(desc(Articles.publishedTime)).limit(5).all()
                #do the same but with bearish articles
                if len(bearish_articles) > 0:
                    userArticles.extend(bearish_articles)
                    #extend if any
            user_articles_data = [{"headline": article.title, "url": article.url} for article in userArticles]
            #format the result
            print(user_articles_data)

            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
            def check(usernm):
                #this is a function checking for correct email format, returning true if correct, false if not
                if(re.fullmatch(regex, str(usernm))):
                    return True
                else:
                    return False
            check(user)
            if check(usernm):
                #if email is of correct format, compose a mail
                if not user_articles_data:
                    #if the user doesn't follow any company, construct the mail only with global stats
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
                    #if the user follows a company, send the global and the personalised updates as well, queried above
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
                    #format it using HTML
                    #iterate through the queried personalised updates, and create a new div for each article
                    #plus, attach the global stats
                    message = f"Subject: Updates\n\n{msgbody}"
                    yag.send(to=usernm, contents=[message])
                    #construct the mail FOR THE CURRENT USER using the composed body and a pre-defined subject - send it using yagmail


#this function is responsible for the Top Gainers, Top Losers and Most Actively Traded updates 
#also utilised by the scheduler, but this is called every 5 minutes to keep the user up to date
def frequentUpdates(): 
    with app.app_context():
        #we drop all 3 tables and create them. This is an efficient approach, since only 1 API call is made to fetch data for all 3 tables
        #plus, for each of these 3 tables, only 20 rows of data is returned, so it is easy to iterate though them and insert
        db.metadata.drop_all(bind=db.engine, tables=[TopGainers.__table__])
        db.metadata.create_all(bind=db.engine, tables=[TopGainers.__table__])
        db.metadata.drop_all(bind=db.engine, tables=[TopLosers.__table__])
        db.metadata.create_all(bind=db.engine, tables=[TopLosers.__table__])
        db.metadata.drop_all(bind=db.engine, tables=[ActivelyTraded.__table__])
        db.metadata.create_all(bind=db.engine, tables=[ActivelyTraded.__table__])
        #utilise the fetch function imported from schema
        topGainersLosersDict = getTopGainersLosers()
        #separate the data accordingly
        topGainers = topGainersLosersDict["top_gainers"]
        topLosers = topGainersLosersDict["top_losers"]
        activelyTraded = topGainersLosersDict["most_actively_traded"]
        
        #iterate through the top gainers
        for gainers in topGainers:
            if gainers != None and gainers != 0:
                #if value is correct, format the change percentage value for insertion and insert. Finally, commit
                print(gainers)
                percent_float = float(gainers["change_percentage"].rstrip('%'))
                db.session.add(TopGainers(gainers["ticker"], gainers["price"], gainers["change_amount"], percent_float, gainers["volume"]))
                db.session.commit()
        
        #iterate through top losers
        for losers in topLosers:
            if losers != None and losers != 0:
                #do the same and insert
                print(losers)
                percent_float = float(losers["change_percentage"].rstrip('%'))
                db.session.add(TopLosers(losers["ticker"], losers["price"], losers["change_amount"], percent_float, losers["volume"]))
                db.session.commit()

        #finally, iterate through the most actively traded
        for active in activelyTraded:
            if active != None and active != 0:
                #do the same, and insert
                print(active)
                percent_float = float(active["change_percentage"].rstrip('%'))
                db.session.add(ActivelyTraded(active["ticker"], active["price"], active["change_amount"], percent_float, active["volume"]))
                db.session.commit()

#this function is responsible for the regular news updates/fetching, to make the user as up to date as possible - also utilized by scheduler
def newsUpdates():
    with app.app_context():
        #get a list of S&P 500 tickers, that we have also utilised in schema
        companies = pd.read_csv('SP_500.csv')
        SPTickers = companies['Symbol'].unique()
        
        #get current date and time, construct variable that points to 30 minutes before
        current_datetime = datetime.now()
        time_from = current_datetime - timedelta(minutes=30)
        formatted_time_from = time_from.strftime("%Y%m%dT%H%M")
        #format a URL utilising alpha vantage news sentiment api arguments:
            #time_from 30 minutes ago
            #we sort by relevance
            #we only want 10
            #and our API key
        url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&time_from={formatted_time_from}&sort=RELEVANCE&limit=10&apikey=QC6PHJMTIZHC8S6B"

        try:
            #make API call, get data
            response = requests.get(url)
            response.raise_for_status()  #this will raise an exception for HTTP errors
            data = response.json()
            #pass it to our function defined above for formatting
            news_items = format_news_feed_data(data)
            print(str(len(news_items))+" IS THE LENGTH OF THE FETCHED UPDATE FEED")
            if news_items:
                #if it contains data
                for newsEntry in news_items:
                    #for every news article
                    if newsEntry:
                        if newsEntry["tickerID"] in SPTickers:
                            #if the ticker is in the S&P 500 tickers
                            whetherExistsQuery = Articles.query.filter_by(title=newsEntry["title"], tickerID=newsEntry["tickerID"]).all()
                            if len(whetherExistsQuery) == 0:
                                #if such article doesn't exist, concatenate the authors and insert
                                authorArr = newsEntry["authors"]
                                authorString = ', '.join(authorArr)
                                news = Articles(newsEntry["tickerID"], newsEntry["title"], newsEntry["url"], newsEntry["publishedTime"], authorString, newsEntry["summary"], newsEntry["bannerImageURL"], newsEntry["source"], newsEntry["category"], newsEntry["sourceDomain"], newsEntry["overallSentiment"])
                                db.session.add(news)

                                #retrieving the current article's ID so we can have multiple sentiments for the current articleID in the ArticleTickers table
                                db.session.flush() 
                                news_id = news.id
                                print("Added for ticker "+str(newsEntry["tickerID"])+" title: "+newsEntry["title"])
                                for sentiment in newsEntry["tickerSentiments"]:
                                    #iterate through the ticker sentiments for the corresponding article
                                    if sentiment:
                                        #insert into ArticleTickers if data exists
                                        sentiments = ArticleTickers(news_id, sentiment["ticker"], sentiment["relevanceScore"], sentiment["sentimentScore"])
                                        db.session.add(sentiments)
                            else:
                                #if article already exist with such title and ticker, ignore, don't insert
                                print("------------IGNORING--------- Already in DB for ticker "+str(newsEntry["tickerID"])+" TITLE: "+newsEntry["title"])
            else:
                #if no news was fetched from the last 30 minutes
                print("EMPTY - NO NEW ARTICLES - DATE AND TIME IS "+str(datetime.now()))
            db.session.commit()
        #handle errors:
        except requests.exceptions.HTTPError as errh:
            logging.error("Http Error: %s", errh)
        except requests.exceptions.ConnectionError as errc:
            logging.error("Error Connecting: %s", errc)
        except requests.exceptions.Timeout as errt:
            logging.error("Timeout Error: %s", errt)
        except requests.exceptions.RequestException as err:
            logging.error("Other Error: %s", err)

#this function is responsible for news deletion
#only deletes old articles from the database that are not saved by any user
#also utilised by the scheduler
def oldNewsDeletion():
    with app.app_context():
        #get all saved articles, get their id's into a list
        savedArticlesQuery = SavedArticles.query.distinct(SavedArticles.id).all()
        savedArticleIDs = [sa.id for sa in savedArticlesQuery]
        #get the day from 5 days ago
        five_days_ago = datetime.now() - timedelta(days=5)
        five_days_ago_day = five_days_ago.day
        #delete entries from Articles where the published day is 5 days ago, and the article's ID is not in the saved articles table (not saved)
        items_five_days_ago = Articles.query.filter((extract('day', Articles.publishedTime) == five_days_ago_day) & not_(Articles.id.in_(savedArticleIDs))).delete()
        if items_five_days_ago > 0:
            print("DELETED OLD NON-SAVED ARTICLES")
        else:
            print("NO NON-SAVED ARTICLES FROM 5 DAYS AGO")
        db.session.commit()
        #this function is called by the scheduler daily, keeping the data in our database consistent, up to date, and non overwhelming


#initialize the scheduler itself, and start it
scheduler = BackgroundScheduler()
scheduler.start()
#add jobs calling the functions above, within the given intervals
scheduler.add_job(frequentUpdates, 'interval', minutes=5)
scheduler.add_job(newsUpdates, 'interval', minutes=30)
scheduler.add_job(dailyUpdates, 'interval', hours=24)
scheduler.add_job(oldNewsDeletion, 'interval', hours=24)


#a custom sanitize function called to sanitize every input field of the page to avoid XSS and SQL injection attacks
def custom_sanitizer(input_from_html):
    #define SQL operators and symbols that might be used to attempt attacks
    chars_to_sanitize = re.compile(r'<[^>]*>')
    sql_operators = ['SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'UNION', 'LIMIT']
    sql_symbols = ['=', '<', '>', '!', ';', "'", '"', '--', '/*', '*/', '&&', '||']
    #combine these operators and symbols
    combined_pattern = '|'.join([chars_to_sanitize.pattern] + [re.escape(op) for op in sql_operators] + [re.escape(sym) for sym in sql_symbols])
    #generate a sanitized string from the input string, replacing any dangerous symbols or operators with an empty string. Return it
    sanitized_html = re.sub(combined_pattern, '', input_from_html)
    return sanitized_html

#an auxiliary function for page restriction and thus security. Check if user is logged in, and returns boolean to react
@app.route('/checkLoggedIn')
def check_logged_in():
    if 'username' in session:
        return jsonify({'loggedIn': True})
    else:
        return jsonify({'loggedIn': False})

@app.route('/')
def home():
    return send_from_directory('static', 'index.html')



#FROM HERE ON OUT, ALL OF THESE ROUTES WILL HANDLE NO RENDER, BUT RATHER HANDLE AN API CALL MADE BY THE REACT FRONTEND.
#THUS, THEY ALL RETURN EITHER THE JSONIFIED DATA NEEDED FOR THE REACT FRONTEND, OR AN ERROR STATUS CODE



#handles saved article call with POST as the article id is passed
@app.route('/saveArticle', methods=["POST"])
def saveArticle():
    try:
        #get the data, extract the ID, and get the logged in user's ID
        data = request.json
        articleID = data.get('id')
        user = session["username"]
        userIDQuery = Users.query.filter_by(email=user).first()
        userIDQuery = userIDQuery.id
        print(str(articleID))
        #create row using these 2 data
        toInsert = [
            SavedArticles(userIDQuery, articleID)
        ]
        db.session.add_all(toInsert)
        #add and commit
        db.session.commit()

        return jsonify({'message': 'Article saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    #return a success message or an error code


#handles following company with POST as the company ticker is passed
@app.route('/follow', methods=["POST"])
def follow():
    try:
        #get data, extract the ticker, get the logged in user and their ID, and capitalize the ticker
        data = request.json
        companyID = data.get('companyId')
        user = session["username"]
        userIDQuery = Users.query.filter_by(email=user).first()
        userIDQuery = userIDQuery.id
        capitalTicker = companyID.upper()
        #create row using these 2 data
        toInsert = [
            UserCompany(userIDQuery, capitalTicker)
        ]
        db.session.add_all(toInsert)
        #add and commit 
        db.session.commit()

        return jsonify({'message': 'accept'})
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    #return a success message or an error code


#handles company unfollow with POST as the company ticker is passed
@app.route('/unfollow', methods=["POST"])
def unfollow():
    try:
        #again, get the data, extract ticker, capitalize it, get current user and their corresponding ID
        data = request.json
        companyID = data.get('companyId')
        user = session["username"]
        userIDQuery = Users.query.filter_by(email=user).first()
        userIDQuery = userIDQuery.id
        capitalTicker = companyID.upper()
        #get the corresponding article
        UserCompany.query.filter_by(user=userIDQuery, company=capitalTicker).delete()
        #delete it and commit
        db.session.commit()
        print("here")
        return jsonify({'message': 'accept'})
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    #return a success message or error code
    

#handles unsave article call with POST as the article id is passed
@app.route('/unsaveArticle', methods=["POST"])
def unsaveArticle():
    try:
        #get the data, extract the ID
        data = request.json
        id = data.get('headline') #this is actually the article ID, not headline
        print(id)
        #get the user in session, retrieve their ID
        user = session["username"]
        userIDQuery = Users.query.filter_by(email=user).first()
        userIDQuery = userIDQuery.id
        #query for the corresponding article, find its ID
        articleIDQuery = Articles.query.filter_by(id=id).first()
        articleID = articleIDQuery.id
        print(userIDQuery)
        print(articleID)
        #delete the row from the savedarticles table where the userID and the articleID match with the given and retrieved values
        SavedArticles.query.filter_by(userID=userIDQuery, articleID=articleID).delete()
        db.session.commit()
        #commit changes

        return jsonify({'message': 'success'})
    except Exception as e:
        print(e)
        return jsonify({'message': str(e)}), 500
    #return success message or error message if failed
        

#handles the saved articles page, returning all saved articles for the user in session - no POST or GET here
@app.route('/returnSavedArticles')
def returnSavedArticles():
    #get the user in session, get their ID
    user = session["username"]
    userIDQuery = Users.query.filter_by(email=user).first()
    userIDQuery = userIDQuery.id
    #query all saved articles for the user
    savedArticlesQuery = SavedArticles.query.filter_by(userID=userIDQuery).all()
    #get all article IDs that the user saved, put them in a list
    newsIDsFollowed = [ns.articleID for ns in savedArticlesQuery]   
    #query for articles corresponding to the article IDs in the list above
    news_query = Articles.query.filter(Articles.id.in_(newsIDsFollowed)).all() 
    #format result (saved articles feed) to return with the attributes from Articles table
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
    #return the jsonified entry - if none, it is handled in frontend
    return jsonify(feed_entries_json)


#handles the home page - all articles from those companies that the user follows - no POST or GET
@app.route('/Homepage')
def homepage():
    #get user in session, retrieve their ID
    user = session["username"]
    userIDQuery = Users.query.filter_by(email=user).first()
    userIDQuery = userIDQuery.id
    #query for rows in the UserCompany table, returning rows corresponding to the userID
    usercompanyquery = UserCompany.query.filter_by(user=userIDQuery).all()
    #extract the company tickers into a list
    company_tickers_followed = [uc.company for uc in usercompanyquery]
    #query articles using the tickers from the list above, in a descending published time
    news_query = Articles.query.filter(Articles.tickerID.in_(company_tickers_followed)).order_by(desc(Articles.publishedTime)).all()
    #format results (home page feed) to return with the attributes from Articles table
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
    #return the jsonified entry - if none, it is handled in frontend
    return jsonify(feed_entries_json)

#fetches data for the AboutCompany page - returns whether the user follows the company displayed or not 
#uses POST - the company ticker is passed
@app.route("/checkFollowStatus", methods=["POST"])
def check_follow_status():
    #get the data, extract the company ticker (not the ID), make it all caps
    data = request.json
    companyId = data.get("companyId")
    #also get the user in session, get their ID
    user = session["username"]
    userIDQuery = Users.query.filter_by(email=user).first()
    userId = userIDQuery.id
    companyId = companyId.upper()
    #find whether a record exists in the UserCompany table, indicating if the user follows the company or not
    recordCount = UserCompany.query.filter_by(user=userId, company=companyId).first() 
    if recordCount is not None:
        #if there is any record, return true (user follows the company)
        is_followed = True
    else:
        #user doesn't follow the company, as there are no results
        is_followed = False
    return jsonify({"isFollowed": is_followed})
    #return the jsonified bool


#handles dynamic updates of a company info, including the CurrentStockPrice table as well as the FinancialData
#Corresponds to the company that the user clicks on - POST request, since we get the company ticker
@app.route('/updateCompany', methods=["POST"])
def updateCompany():
    #get the data, extract company ticker, make it all caps
    data = request.json
    companyId = data.get("companyId")
    #also get the user in session, get their ID
    user = session["username"]
    userIDQuery = Users.query.filter_by(email=user).first()
    userId = userIDQuery.id
    companyId = companyId.upper()
    #call 2 functions defined in the schema - they fetch information on the requested company using its ticker
    data1 = get_company_overview(companyId)
    data2 = get_current_stock_price_and_volume(companyId)
    #get todays date
    timestamp = datetime.now()
    if data1:
        if data2:
            #if both values are correct, query the CurrentStockPrice table for the corresponding company - prepare for update
            stockQuery = CurrentStockPrice.query.filter_by(tickerID=companyId).first()
            #update the given values for the company in the table
            stockQuery.stockPrice = data2["Current Price"]
            stockQuery.volumeOfTrade = data2["Current Volume"]
            stockQuery.timestamp = timestamp

            #query the FinancialData table for the corresponding company - prepare for update
            financialQuery = FinancialData.query.filter_by(tickerID=companyId).first()
            #handle errors! As the API call may not always return actual data from the API URL, we have to check for empty values and handle them accordingly
            #this means updating them with default values for the given attribute types
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
            #but if the values are correct, update the corresponding values extracted from the function

            db.session.commit()

    return jsonify({"message": "success"})
    #commit changes, return success message - errors handled above and frontend

   
#handles similar company section for About Company page with POST as the company ticker is passed
@app.route('/similarCompany', methods=["POST"])
def similarCompany():
    #get the data, extract ticker, make it all caps
    data = request.json
    companyId = data.get("companyId")
    companyId = companyId.upper()
    print(str(companyId)+" is the company ID")
    #get the user in session, retrieve their ID - not used here
    user = session["username"]
    userIDQuery = Users.query.filter_by(email=user).first()
    userId = userIDQuery.id
    #query from the Company table for the given company ticker
    companyQuery = Company.query.filter_by(ticker=companyId).first()
    #extract sector and industry values
    sector = companyQuery.sector
    industry = companyQuery.industry
    #make a query in the Company table where the searched company's industry and sector is the same as the given company's
    #exclude the current company, plus limit the results to 5
    similarQuery = Company.query.filter(Company.industry==industry, Company.sector==sector, not_(Company.ticker == companyId)).limit(5).all()
    #if the results are less than 5...
    if len(similarQuery) < 5:
        #only query where the sector is the same as in the current company - query as much as needed to query 5 TOTAL companies
        additional_companies = Company.query.filter(Company.sector == sector, not_(Company.industry == industry)).limit(5-len(similarQuery)).all()
        #extend our original query
        similarQuery.extend(additional_companies)
        if len(similarQuery) < 5:
            #if the length is still less than 5, only query where the industry is the same as in the current company - again, query to make it 5 companies in total
            more_query = Company.query.filter(not_(Company.sector == sector), Company.industry == industry).limit(5-len(similarQuery)).all()
            #extend our query with the results
            similarQuery.extend(more_query)
    #format the results from the (possibly extended) query
    names = [
        {"name": entry.name,
         'ticker': entry.ticker
        }
        for entry in similarQuery
    ]
    
    return (jsonify(names))
    #return the jsonified result of similar companies


#handles related news for the About Company page with POST as the article ticker is passed
@app.route('/relatedNews', methods=["POST"])
def relatedNews():
    #get data, extract ticker, make it all caps
    data = request.json
    companyId = data.get("companyId")
    companyId = companyId.upper()
    print(str(companyId)+" is the company ID")
    #get user in session, get their ID
    user = session["username"]
    userIDQuery = Users.query.filter_by(email=user).first()
    userId = userIDQuery.id
    #make a query from articles where the company ticker matches with the ticker from the POST, limit it to 3 and order by freshest first
    #this will display "related news", meaning, news corresponding to the current company only
    relatedQuery = Articles.query.filter(Articles.tickerID==companyId).order_by(desc(Articles.publishedTime)).limit(3).all()
    #format results
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
    #return the jsonified result of related news


#handles the companies part of the results page upon search - POST as we pass on the search string
@app.route('/searchCompany', methods=["POST"])
def searchCompany():
    #get the data, extract the string, make it all lowercase
    data = request.json
    stringd = data.get("string")
    string = stringd.lower()
    #SANITIZE input using our function defined above
    string = custom_sanitizer(string)
    print(string+" IS OUR STRING")
    #query companies where the company name starts with the string, or the ticker contains the string (ticker might be different than the company name)
    #limit results to 5
    companyname_starts_with = Company.query.filter(or_(func.lower(Company.name).startswith(string), func.lower(Company.ticker).contains(string))).limit(5).all()
    companies = companyname_starts_with
    if len(companies) == 0:
        #if no results, handle that by sending a message indicating empty query
        return (jsonify({"message": "empty"}))
    for elem in companies:
        print(elem.name+" IS A COMPANY")
    #otherwise, if there are results, format them
    companyList = [
        {"name": entry.name,
         "ticker": entry.ticker,
         "sector": entry.sector,
         "industry": entry.industry
        }
        for entry in companies
    ]
    return (jsonify(companyList))
    #return the formatted jsonified list


#handles the articles part of the results page upon search - POST as we pass on the search string
@app.route('/searchHeadline', methods=["POST"])
def searchHeadline():
    #get data, extract search string, make it all lowercase
    data = request.json
    stringd = data.get("string")
    string = stringd.lower()
    #SANITIZE it using our function defined above
    string = custom_sanitizer(string)
    #query for articles where the article title contains the search keyword/string, make it the freshest first, and limit it to 20
    articles = Articles.query.filter(func.lower(Articles.title).contains(string)).order_by(desc(Articles.publishedTime)).limit(20).all()
    if len(articles) == 0:
        #if there are no results, handle that by sending a message indicating empty query
        return (jsonify({"message": "empty"}))
    for elem in articles:
        print(elem.title+" IS A TITLE")
        print(str(elem.id)+" IS THE CORRESPONDING ID")
    #format results - MAY CONTAIN DUPLICATES
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


    #TO HANDLE DUPLICATES, we have implemented the following:
    #first have an initial empty dictionary
    merged_entries = {}
    for entry in articles:
        #for every row in the query, grab the title
        article_key = (entry.title)
        if article_key in merged_entries or entry.id in merged_entries:
            # If the article title already exists, append the ticker into the array of tickers for the corresponding entry in merged_entries
            merged_entries[article_key]['ticker'].append(entry.tickerID)
        else:
            #if there are no "duplicates" (similar titled articles), append this as a new record
            if entry.bannerImageURL is not None or entry.bannerImageURL == "":
                #format entry in the dict: if there is a banner image, use that
                merged_entries[article_key] = {
                    "id": entry.id,
                    "ticker": [entry.tickerID],
                    "title": entry.title,
                    "url": entry.url,
                    "source": entry.source,
                    "summary": entry.summary,
                    "image": entry.bannerImageURL,
                    "sentiment": entry.overallSentiment,
                    "time": entry.publishedTime
                }
            else:
                #if there is no image for the entry, place a custom image for visual consistency - format the entry like so:
                #the image is from Pixabay, which offers free to use, no copyright images, hence the usage for articles that don't have a banner imgage url
                print("IMAGE FOR ENTRY ID: "+str(entry.id)+" IS NONEXISTENT. PLACING UNIQUE IMAGE")
                merged_entries[article_key] = {
                    "id": entry.id,
                    "ticker": [entry.tickerID],
                    "title": entry.title,
                    "url": entry.url,
                    "source": entry.source,
                    "summary": entry.summary,
                    "image": "https://cdn.pixabay.com/photo/2013/07/12/19/16/newspaper-154444_960_720.png",
                    "sentiment": entry.overallSentiment,
                    "time": entry.publishedTime
                }
    feed_entries_json = list(merged_entries.values())
    #make a list of the values in the dict, and return the jsonified result
    return jsonify(feed_entries_json)


#fetched to determine whether an article is saved or not - POST as it takes the article ID
@app.route("/checkSaveStatus", methods=["POST"])
def check_save_status():
    #get the data, extract the article ID
    data = request.json
    articleId = data.get("articleID")
    #get the user in session, get their ID
    user = session["username"]
    userIDQuery = Users.query.filter_by(email=user).first()
    userId = userIDQuery.id
    #query for saved articles where the userID and the articleID match with the received & queried values
    recordCount = SavedArticles.query.filter_by(userID=userId, articleID=articleId).first() 
    if recordCount is not None:
        #if there is a record, the article is saved for the user, return true
        is_saved = True
    else:
        #else it is not saved, return false
        is_saved = False
    return jsonify({"isFollowed": is_saved})
    #jsonify the boolean


#handles the Followed Companies page - no POST or GET
@app.route('/followedCompanies')
def followedCompanies():
    #get the user in session, get their ID
    user = session["username"]
    userIDQuery = Users.query.filter_by(email=user).first()
    userIDQuery = userIDQuery.id
    #query all rows from UserCompany where the userID matches with the current user's id
    usercompanyquery = UserCompany.query.filter_by(user=userIDQuery).all()
    #make a list of tickers corresponding to companies followed by the user
    company_ticker_query = [uc.company for uc in usercompanyquery]
    #query all companies from Company table where the ticker is in this list above
    company_query = Company.query.filter(Company.ticker.in_(company_ticker_query)).all()
    print("Length of query is "+str(len(company_query)))
    #format the results
    company_entries_json = [
        {"companyName": entry.name,
         "companyTicker": entry.ticker,
         "sector": entry.sector,
         "industry": entry.industry
        }
        for entry in company_query
    ]
    return jsonify(company_entries_json)
    #return the jsonified list - empty list is handled in frontend


#handles the discover page
#POST if filters are received from the discover page
#GET if there are no filters received (default)
@app.route('/Discover', methods = ['POST', 'GET'])
def discover():
    if request. method == 'POST':
        #if filters are toggled and applied...
        #get the data about which filters are ticked (an array of booleans)
        data = request.json
        true_values = data.get('trueValues', [])
        offset = data.get('trimLengthOffset')
        print(str(offset)+" IS THE OFFSET")
        #pre-define categories, as they are static (also pre-defined in the Discover's frontend page)
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
        #pre-define sectors, as they are static (also pre-defined in the Discover's frontend page)
        sector = [
            "ENERGY & TRANSPORTATION",
            "FINANCE",
            "LIFE SCIENCES",
            "MANUFACTURING",
            "REAL ESTATE & CONSTRUCTION",
            "TECHNOLOGY",
            "TRADE & SERVICES"
        ]
        #initialize 2 empty list, one for the sectors, one for the categories
        sectorlist = []
        categorylist = []
        publishDate = 0 
        #0 is publish date by ascending order, 1 was descending
        #parse the data received in the POST request body
        for item in true_values:
            #get the current key-index pair, where key is either "category" or "sector"
            #index is the index for the true value corresponding to the index in the pre-defined sector or category lists
            key = item.get('key')
            index = item.get('index')
            if key == "category":
                #if it is category
                if category[index] == "General":
                    #we merged the category General with the following categories: n/a, GoogleRSS, BusinessGoogleRSS
                    #reason is that the average user will not know what GoogleRSS or BusinessGoogleRSS even means
                    #plus half of the data has n/a as category
                    #so append the following values into the category list
                    categorylist.append("n/a")
                    categorylist.append("GoogleRSS")
                    categorylist.append("BusinessGoogleRSS")
                categorylist.append(category[index])
                #append General as well into the category list, if not, append the type of category
                
            elif key == "sector":
                #append the corresponding value at the given index into the sector list
                sectorlist.append(sector[index])
            elif key == "publishDate":
                #get the publish date if the key is "publishDate"
                publishDate = index
        for elem2 in categorylist:
            print(elem2)
        for elem in sectorlist:
            print(elem)
        print(publishDate)
        
        #query Companies where the company's sector matches with any of the sectors from sectorList (sectors ticked by the user)
        sectorQuery = Company.query.filter(Company.sector.in_(sectorlist)).all()
        #make a list of tickers corresponding to these companies
        tickerIDForSector = [comp.ticker for comp in sectorQuery]
        if publishDate == 0:
            #if ascending order, make a query where we BOTH query for records where 
                #1) the ticker matches with the ticker in the list of tickers corresponding to companies for the selected sectors, and
                #2) the category matches with any of the categories in the category list
            sectorQueryArticles = Articles.query.filter(and_(Articles.tickerID.in_(tickerIDForSector), Articles.category.in_(categorylist))).order_by(asc(Articles.publishedTime)).offset(0).all()
        else:
            #if descending order, do the same but descending by published time
            sectorQueryArticles = Articles.query.filter(and_(Articles.tickerID.in_(tickerIDForSector), Articles.category.in_(categorylist))).order_by(desc(Articles.publishedTime)).offset(0).all()

        counter = 0
        for elem in sectorQueryArticles:
            counter = counter + 1
        print(counter)

        #if no sectors are selected...
        if sectorlist == []:
            #if no categories are selected
            if categorylist == []:
                #if descending order
                if publishDate == 1:
                    #basically query all articles but in descending order (=Discover feed but descending by published time)
                    sectorQueryArticles = Articles.query.order_by(desc(Articles.publishedTime)).offset(0).all()
                else:
                    #basically query all articles but in ascending order (=Discover feed but ascending by published time)
                    sectorQueryArticles = Articles.query.order_by(asc(Articles.publishedTime)).offset(0).all()
            else:
                #if only the sector list is empty, treat none selected as all selected - this way, we know that the user only wants to filter by category
                if publishDate == 1:
                    #only check for category matches - descending order
                    sectorQueryArticles = Articles.query.filter(Articles.category.in_(categorylist)).order_by(desc(Articles.publishedTime)).offset(0).all()
                else:
                    #only check for category matches - ascending order
                    sectorQueryArticles = Articles.query.filter(Articles.category.in_(categorylist)).order_by(asc(Articles.publishedTime)).offset(0).all()
        else:
            if categorylist == []:
                #but if the category list is empty... user only cares about sectors
                if publishDate == 1:
                    #only check for sector matches - descending order 
                    sectorQueryArticles = Articles.query.filter(Articles.tickerID.in_(tickerIDForSector)).order_by(desc(Articles.publishedTime)).offset(0).all()
                else:
                    #only check for sector matches - ascending order
                    sectorQueryArticles = Articles.query.filter(Articles.tickerID.in_(tickerIDForSector)).order_by(asc(Articles.publishedTime)).offset(0).all()

        #we would still need to merge the entries
        #EVERYTHING IS EXACTLY THE SAME AS FOR /searchHeadline, except we do "for entry in *sectorQueryArticles*"
            #we want to merge from our previous query
        merged_entries = {}
        for entry in sectorQueryArticles:
            article_key = (entry.title)
            if article_key in merged_entries or entry.id in merged_entries:
                # If the article key exists, append the ticker
                merged_entries[article_key]['company'].append(entry.tickerID)
            else:
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
        feed_entries_json = list(merged_entries.values())
        return jsonify(feed_entries_json)
        #return the jsonified list of articles
    else:
        #if the method was GET
        #meaning, it is the discover page without the filters
        #retrieve arguments (or initialize limit with value 10 and offset with value 0) which are:
            #1) limit, 2) offset (which row the query starts from) 
        #offset is utilised for the "more" button in the discover feed
        num_articles = request.args.get('limit', type=int) or 10
        offset = request.args.get('offset', type=int) or 0
        #simply query from Articles using the received arguments
        news_query = Articles.query.order_by(desc(Articles.publishedTime)).limit(num_articles).offset(offset).all()

        '''
        session method could theoretically work for keeping track of articles BEFORE the "more" button was clicked BUT:
            how does it merge About Company buttons for a headline corresponding to multiple companies (tickers) if, for one, 
            offset is 0 (loaded initially), and for the other, offset is, say, 10? If session implementation is correct, it won't just "add"
            the company name ALSO corresponding to a previously shown article to that article, but rather will just ignore it

        THIS RIGHT HERE is the current possible best implementation within the time frame, other requirements and 
        the unimportance of perfecting this already good implementation
        '''

        #again, merge the entries
        #SAME EVERYTHING but we go through the news_query from before
        merged_entries = {}
        
        for entry in news_query:
            article_key = (entry.title)
            if article_key in merged_entries or entry.id in merged_entries:
                merged_entries[article_key]['company'].append(entry.tickerID)
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
        feed_entries_json = list(merged_entries.values())
        return jsonify(feed_entries_json)
        #return the jsonified list of articles


#handles fetching top gainers for home page
@app.route('/fetchgainer')
def fetchgainer():
    #simply grab the 5 (already sorted) top gainers from the TopGainers table
    gainers_query = TopGainers.query.limit(5).all()
    #format it
    feed_entries_json = [
        {"company": entry.ticker,
        "value": round(entry.changePercent, 2),
        }
        for entry in gainers_query
    ]
    return jsonify(feed_entries_json)
    #return the jsonified list of top gainers

#handles fetching top losers for home page
@app.route('/fetchloser')
def fetchloser():
    #simply grab the 5 (already sorted) top losers from the TopLosers table
    losers_query = TopLosers.query.limit(5).all()
    #format it
    feed_entries_json = [
        {"company": entry.ticker,
        "value": round(entry.changePercent, 2),
        }
        for entry in losers_query
    ]
    return jsonify(feed_entries_json)
    #return the jsonified list of top gainers

#handles fetching most actively traded companies for home page
@app.route('/fetchmostactive')
def fetchmostactive():
    #simply grab the 5 (already sorted) most actively traded from the ActivelyTraded table
    active_query = ActivelyTraded.query.limit(5).all()
    #format it
    feed_entries_json = [
        {"company": entry.ticker,
        "value": round(entry.volume, 2),
        }
        for entry in active_query
    ]
    return jsonify(feed_entries_json)
    #return the jsonified list of most actively traded companies


#handles About Company page for a company - POST as the ticker is passed on as parameter
#retrieved only after the data for the company is loaded/updated on clicking the company
@app.route('/retrieveCompany', methods=["POST"])
def retrieveCompany():
    #get the data, extract ticker, make it all caps
    data = request.json
    ticker = data.get('companyId')
    capitalTicker = ticker.upper()
    print(capitalTicker)
    #query the Companies table, the CurrentStockPrice table and the FinancialData table for the given company
    companyQuery = Company.query.filter_by(ticker=capitalTicker).first()
    stockQuery = CurrentStockPrice.query.filter_by(tickerID=capitalTicker).first()
    financialQuery = FinancialData.query.filter_by(tickerID=capitalTicker).first()
    #round the numeric data displayed on the website for consistency and better user experience
    roundStock = round(stockQuery.stockPrice, 2)
    roundVolume = round(stockQuery.volumeOfTrade, 2)
    roundCap = round(financialQuery.marketCap, 2)
    roundPe = round(financialQuery.pe_ratio, 2)
    roundEps = round(financialQuery.eps, 2)
    roundRoe = round(financialQuery.roe, 2)

    #format the data for a company using the 3 tables, using the appropriate rounded values above as well
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
    #return the jsonified data about the requested company


#handles logging into the website
@app.route('/submitlogin', methods=['POST', 'GET'])
def login():
    #get data, extract username and password
    data = request.json
    email = data.get('username')
    passwd = data.get('password')
    #SANITIZE both input field data using our custom sanitizer function defined above
    email = custom_sanitizer(email)
    passwd = custom_sanitizer(passwd)
    #check if user exists
    users = Users.query.filter_by(email=email).first()
    useractivated = users.isactivated
    #if there are no such users, respond with "deny"
    if users == None:
        response_message = 'deny'
    #if the hash of the given password doesn't match with the stored password has, respond with "deny"
    if not security.check_password_hash(users.hashed_password, passwd): 
        response_message = 'deny'
    else:
        #if the user is not activated (future improvement), respond with "deny"
        if useractivated == 0:
            response_message = 'deny'
        else:
            #if user is activated, there are no such users in the db, and the password is correct, respond with "accept"
            #plus, put their email address in the session used in mostly all of the routes in the backend
            response_message = 'accept'
            session['username'] = email
            
    return jsonify({'message': response_message})
    #return the response jsonified
    

#handle logout
@app.route('/logout')
def logout():
    try:
        #delete the session
        del session['username']
    except KeyError:
        pass
    #pop the user from the session and clear the session
    session.pop('username', None)
    session.clear()
    #return a success message
    return jsonify({'message': 'Logout successful'}), 200


#handles signing up to the website - uses POST as 3 values are passed
@app.route('/submitsignup', methods=['POST', 'GET'])
def submitsignup():
    #first get the data, extract the 3 fields: email, password, and password repeated
    data = request.json
    usernm = data.get('email')
    #sanitize email and password fields with our sanitizer function defined above, as password repeated field is hashed
    usernm = custom_sanitizer(usernm)
    passwd = data.get('password')
    hashed_pwd = generate_password_hash(passwd)
    passwordre = data.get('confirmPassword')
    passwordre = custom_sanitizer(passwordre)
    token = srializer.dumps(usernm, salt='email-confirm')
    
    #query for such an user
    users = Users.query.filter_by(email=usernm).first()

    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    def check(usernm):
        #an email format checking function
        if(re.fullmatch(regex, usernm)):
            return True
            #returns true if the email is of correct format, false otherwise
        else:
            return False
    
    check(usernm)

    if check(usernm):
            #if email has correct format
            if users == None:
                #if there are no such users
                if passwd == passwordre:
                    #if password matches with the hashed password, add the user to the DB and commit, return "accept" as status
                    all_users = [
                        Users(usernm,hashed_pwd,token, 1), 
                    ]
                    db.session.add_all(all_users)
                    db.session.commit()
                    response_message = 'accept'
                else:
                    #if passwords don't match, return "deny"
                    response_message = 'deny'
            else:
                #if there is such a user already, return "deny"
                response_message = 'deny'
    else:
        #if email is not of correct format, return "deny"
        response_message = 'deny'
            
    return jsonify({'message': response_message})
    #return the status of the signup

