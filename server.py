#"flask run" in terminal
#I have some basic email (username) and password pairs, so you don't have to mess around with tsting the signup verification (me and Rachel will handle it):
    #Tasneem - Tasneem
    #Danyal - Danyal
    #Rachel - Rachel
    #Michael - Michael
    #Marios - Marios
    #rikifekete2003@gmail.com - erikpwd (mine)

import os
from flask import Flask, request, redirect, render_template, url_for, session
app = Flask(__name__)
app.secret_key = 'incredibly secret key of ours'
from datetime import datetime, timedelta
from werkzeug import security
from markupsafe import escape
from sqlalchemy import and_, or_
from flask_mail import Mail, Message
import re #for the signup page
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import yagmail 
from schema import db, dbinit, Users
from flask_sqlalchemy import SQLAlchemy
srializer = URLSafeTimedSerializer('xyz567')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30) 
#session is going to terminate after 30 minutes
mail = Mail(app)
db.init_app(app)

resetdb = True
if resetdb:
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

@app.route('/')
def home():
    if 'username' in session:
        username = session['username']
        return render_template('index.html', username=username)
    else:
        return redirect('/login')

@app.route('/login')
def loginpage():
    if 'username' in session:
        return redirect('/')
    return render_template('login.html')

@app.route('/submitlogin', methods=['POST', 'GET'])
def login():
    
    if request.method == 'POST':
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
              return '<p>Your account is not activated. Another email was sent to you to verify your address</p><br /><p>The email you entered is {}. The token is {}</p><br /><p>Activate your account in an hour. If you cant, you can receive a new confirmation email on a login attempt</p>'.format(email, token)
            elif useractivated == 1:
              return redirect('/')

@app.route('/logout')
def logout():
    try:
        del session['username']
    except KeyError:
        pass
    session.pop('username', None)
    session.clear()
    return redirect('/login')

@app.route('/signup')
def signup():
    if 'username' in session:
        return redirect('/') #if it is in session, login will redirect them to main page, so no need to change in 2 places if modifying
    else:
        return render_template('signup.html')
    

@app.route('/submitsignup', methods=['POST', 'GET'])
def submitsignup():
    

    
    usernm = request.form.get("email")
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

                    return '<p>The email you entered is {}. </p><br /><p>Activate your account in an hour. If you cant, you can receive a new confirmation email on a login attempt</p>'.format(usernm)
                else:
                    return "Passwords should match. Try again!"
            else:
                return "User already exists! Please choose a different username!"
        else:
            return "Invalid email format. Try again!"
@app.route('/confirmemail/<token>')
def confirmemail(token):
  email = srializer.loads(token, salt='email-confirm', max_age=3600)
  users = Users.query.filter_by(email=email).first()
  users.isactivated = 1
  db.session.commit()
  return '<p>Yay, {}, you have just activated your email!</p><form action="/"><input type="submit" value="Return to login"></form>'.format(email)