from flask import Flask, redirect, render_template, url_for, request
from flask_wtf import FlaskForm
#from werkzeug import secure_filename
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from wtforms.validators import Email, InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import numpy as np
import MySQLdb
import pandas as pd
#from flask_mail import Mail, Message

#deadline='28-Sep-2021'

question_bank = pd.read_csv(r"C:/Users/ADMIN/Documents/Codebase/Interview_chatbot/Question_bank.csv")

app = Flask(__name__)
#mail = Mail(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secretkey123'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['UPLOAD_FOLDER'] = '/uploads_interviewbot/'
#app.config['MAX_CONTENT_PATH'] = '1000000'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# configuration of mail
# app.config['MAIL_SERVER']='smtp.gmail.com'
# app.config['MAIL_PORT'] = 465
# app.config['MAIL_USERNAME'] = 'testing.interviewbot@gmail.com'
# app.config['MAIL_PASSWORD'] = 'pass*123'
# app.config['MAIL_USE_TLS'] = False
# app.config['MAIL_USE_SSL'] = True
# mail = Mail(app)

# Configuration for MySQL database for storing aspirant data:
hostName = 'db4free.net'      
userName = 'udreedbczu'          
passWord = 'ezcb9vazqz'           
dbName =  userName                
DBConn= MySQLdb.connect(hostName,userName,passWord,dbName)

def runCMD (DDL):
    
    """

    MySQL function for CUD of CRUD

    """

    DBConn= MySQLdb.connect(hostName,userName,passWord,dbName)
    myCursor = DBConn.cursor()
    retcode = myCursor.execute(DDL) 
    print (retcode)
    DBConn.commit()
    DBConn.close()

def runSELECT (CMD):
    
    """

    MySQL function for R of CRUD

    """

    DBConn= MySQLdb.connect(hostName,userName,passWord,dbName)
    df_mysql = pd.read_sql(CMD, con=DBConn)    
    DBConn.close()
    return df_mysql

def r(msg):
    
    """

    This function automatically routes all SQL operations to runCMD or runSELECT automatically
    
    """
    
    if msg[0:6]=="SELECT" or msg[0:6]=="select":
        return runSELECT(msg)
    else:
        runCMD(msg)

@app.before_first_request
def create_tables():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view="login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

db = SQLAlchemy()
class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class RegisterForm(FlaskForm):
    username = StringField('username',validators=[InputRequired(), Length(min=0, max=100)])
    password = PasswordField('password',validators=[InputRequired(), Length(min=4, max=100)])
    submit = SubmitField("Sign up")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username = username.data).first()
        if existing_user_username:
            raise ValidationError(
                "That username already exists."
            )

class LoginForm(FlaskForm):
    username = StringField('username',validators=[InputRequired(), Length(min=0, max=100)])
    password = PasswordField('password',validators=[InputRequired(), Length(min=4, max=100)])
    submit = SubmitField("Log In")

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/dashboard", methods=["GET","POST"])
@login_required
def dashboard():
    #Interview instructions
    return render_template('dashboard.html')

login_provided_by_aspirant=''
user_topics = ''

@app.route("/interview", methods=["GET","POST"])
@login_required
def interview():
    #Taking the interview
    print("*"*30)
    print(login_provided_by_aspirant)
    print("*"*30)
    print(user_topics)
    data=[
         {'q1':'a','q2':'b','q3':'c'},
         {'q1':'a','q2':'b','q3':'c'},
         {'q1':'a','q2':'b','q3':'c'}        
    ]
    
    return render_template("interview.html", uname=login_provided_by_aspirant, topics=user_topics, data = data)

@app.route("/login", methods=["GET","POST"])
def login():
    form = LoginForm()
    # print("Printing before login form is validated")
    if form.validate_on_submit():
        # print("Printing after login form is validated")
        user = User.query.filter_by(username=form.username.data).first()
        # print(f"Form input {form.username.data}")
        # print(f"User is {user}")

        if user:
            # print(f"User {user} found")
            if bcrypt.check_password_hash(user.password, form.password.data):
                # user.authenticated = True  #@@
                # db.session.add(user)  #@@
                # db.session.commit()   #@@
                global login_provided_by_aspirant
                global user_topics
                login_provided_by_aspirant = form.username.data
                user_topics = r(f"select topics from aspirant_topics where login='{login_provided_by_aspirant}'").iloc[0,0]
                print("*"*30)
                print(login_provided_by_aspirant)
                print("*"*30)
                print(user_topics)
                login_user(user)
                return redirect(url_for("dashboard"))
        else:
            return redirect(url_for("home"))

    return render_template("login.html", form=form)

@app.route("/register", methods=["GET","POST"])
def register():
    form = RegisterForm()
    # print("Printing before registration form is validated")

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password = hashed_password)
        # print("Printing after registration form is validated")
        # print(form.username.data)
        # print(hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form) 

@app.route("/successt")
def successt():
    return render_template("successt.html")

@app.route("/logout", methods=["GET","POST"])
@login_required
def logout():
    logout_user()
    # user = current_user  #@@
    # user.authenticated = False  #@@
    # db.session.add(user)  #@@
    # db.session.commit()  #@@
    return redirect(url_for('home'))

if __name__=="__main__":
    app.run(debug=True)

