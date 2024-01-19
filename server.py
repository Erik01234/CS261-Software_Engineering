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

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

mail = Mail(app)
srializer = URLSafeTimedSerializer('xyz567')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30) #session is going to terminate after 30 minutes


from schema import db, dbinit, Users

db.init_app(app)

resetdb = False
if resetdb:
    with app.app_context():
        db.drop_all()
        db.create_all()
        #dbinit() - inside the schema

@app.route('/')
def home():
    if 'username' in session:
        username = session['username']
        return render_template('index.html', username=username)
    else:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    
    if request.method == 'POST':
        passwd = request.form.get("email")
        passwd = escape(passwd)
        email = request.form.get("password")
        email = escape(email)
        session["username"] = email
        users = Users.query.filter_by(email=email).first()
        useractivated = Users.query.filter_by(email=email).first().isactivated
        if users == None:
            return "Incorrect email. Try again!"
        if not security.check_password_hash(users.password, passwd):
            return "Incorrect password. Try again!"
        else:
            if useractivated == 0:
              token = srializer.dumps(email, salt='email-confirm')
              msg = Message('Confirm Email', sender='rikifekete2003@gmail.com', recipients=[email])
              link = url_for('confirmemail', token=token, external=True)
              msg.body = 'Your link is {}'.format(link)
              mail.send(msg)
              users.temptoken = token
              db.session.commit()
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
        return redirect('/login') #if it is in session, login will redirect them to main page, so no need to change in 2 places if modifying
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
            isvalid = 1
            return True
        else:
            return False
            print("Invalid email")
    
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
                    session["user"] = usernm
                    msg = Message('Confirm Email', sender='rikifekete2003@gmail.com', recipients=[usernm])
                    link = url_for('confirmemail', token=token, external=True)
                    urlbeginning = request.base_url
                    urlnew = urlbeginning+link
                    urlnew = urlnew.replace("/addregister", "")
                    msg.body = 'Your link is {}'.format(urlnew)
                    mail.send(msg)
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