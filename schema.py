from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

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
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
        # is the 1/2/3/4 letter code of the company that is on the stock market - CAN ALSO BE THE PRIMARY KEY, since it is uniique

    def __init__(self, name):
        self.name = name

class UserCompany(db.Model): 
    #stores which users are following which company - a simple pairing
    __tablename__ = 'usercompany'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Text())
    company = db.Column(db.Text())

    def __init__(self, user, company):
        self.user = user
        self.company = company

class News(db.Model):
    #stores news, need to figure out the columns here (WHAT we want to store about the news) - important part
    __tablename__ = 'news'

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