#"flask run" in terminal
#I have some basic email (username) and password pairs, so you don't have to mess around with tsting the signup verification (me and Rachel will handle it):
    #Tasneem - Tasneem
    #Danyal - Danyal
    #Rachel - Rachel
    #Michael - Michael
    #Marios - Marios
    #rikifekete2003@gmail.com - erikpwd (mine)

import os
from flask import Flask, request, redirect, render_template, url_for, session, send_from_directory, jsonify
app = Flask(__name__, static_url_path="/static")
app.secret_key = 'incredibly secret key of ours'
from datetime import datetime, timedelta
from werkzeug import security
from markupsafe import escape
from sqlalchemy import and_, or_, not_
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
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30) 
import pandas as pd
#session is going to terminate after 30 minutes
mail = Mail(app)
db.init_app(app)



resetwholedb = False
if resetwholedb:
    with app.app_context():
        db.drop_all()
        db.create_all()
        dbinit()



#if we only want to reset/refill individual tables with data...
#have to definie a separate function in schema only containing the imports into that specific table only, and import it in this server file
resetNews = False
if resetNews:
    with app.app_context():
        db.metadata.drop_all(bind=db.engine, tables=[Articles.__table__])
        db.metadata.create_all(bind=db.engine, tables=[Articles.__table__])
        db.metadata.drop_all(bind=db.engine, tables=[ArticleTickers.__table__])
        db.metadata.create_all(bind=db.engine, tables=[ArticleTickers.__table__])
        fillUpNews()

with open('smtp_credentials.txt', 'r') as file:
    app_pwd = file.read() 
    #app specific password, not my actual gmail password

gmail_user = "rikifekete2003@gmail.com"
gmail_password = app_pwd 
yag = yagmail.SMTP(gmail_user, gmail_password, host="smtp.gmail.com")


companies = pd.read_csv('SP_500.csv')
tickers = companies['Symbol'].unique()
def frequentUpdates():

    for ticker in tickers:
        with app.app_context():
            currentCurrent = CurrentStockPrice.query.filter_by(tickerID=ticker).first()
            if currentCurrent and currentCurrent.tickerID:
                stockPriceList = get_current_stock_price_and_volume(ticker)
                currentCurrent.timestamp = datetime.now()
                currentCurrent.stockPrice = stockPriceList["Current Price"]
                currentCurrent.volumeOfTrade = stockPriceList["Current Volume"]
                db.session.commit()

def dailyUpdates():
    #UPDATE FINANCIAL DATA TABLE
    print("Daily update initiated.")
    
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(frequentUpdates, 'interval', hours=24)
scheduler.add_job(dailyUpdates, 'interval', hours=24)


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
    

    

@app.route('/unsaveArticle', methods=["POST"])
def unsaveArticle():
    try:
        data = request.json
        headline = data.get('headline')
        print(headline)
        user = session["username"]
        userIDQuery = Users.query.filter_by(email=user).first()
        userIDQuery = userIDQuery.id
        articleIDQuery = Articles.query.filter_by(title=headline).first()
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
        "source": entry.url,
        "time": entry.publishedTime,
        "icon": entry.bannerImageURL,
        "logo": entry.bannerImageURL,
        "company": entry.tickerID,
        "summary": entry.summary,
        "sentiment": entry.overallSentiment
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
    news_query = Articles.query.filter(Articles.tickerID.in_(company_tickers_followed)).all()
    #news_query = Articles.query.all()
    feed_entries_json = [
        {"headline": entry.title,
        "source": entry.url,
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
    '''
    to update:
        timestamp;
        stockprice;
        volume;
        marketcap;
        pe;
        eps;
        roe
    '''
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
            financialQuery.marketCap = data1["MarketCapitalization"]
            financialQuery.pe_ratio = data1["PERatio"]
            financialQuery.eps = data1["EPS"]
            financialQuery.roe = data1["ROE"]

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
    news_query = Articles.query.all()
    #news_query = Articles.query.all()
    feed_entries_json = [
        {"headline": entry.title,
        "source": entry.url,
        "time": entry.publishedTime,
        "icon": entry.bannerImageURL,
        "logo": entry.bannerImageURL,
        "company": entry.tickerID,
        "id": entry.id,
        'summary': entry.summary,
        'sentiment': entry.overallSentiment
        }
        for entry in news_query
    ]
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


'''@app.route('/login')
def loginpage():
    if 'username' in session:
        return redirect('/')
    return render_template('login.html')'''


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
        "roe": roundRoe
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

@app.route('/signup')
def signup():
    if 'username' in session:
        return redirect('/') #if it is in session, login will redirect them to main page, so no need to change in 2 places if modifying
    else:
        return render_template('signup.html')
    

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
    passwd = data.get('password')
    hashed_pwd = generate_password_hash(passwd)
    passwordre = data.get('confirmPassword')
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

'''

/aboutCompany
/articleAnalysis
/followedCompanies
/savedArticles
/loginPage
/homePage
/navbar

'''