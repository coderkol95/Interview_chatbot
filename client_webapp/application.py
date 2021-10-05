from flask import Flask, redirect, render_template, url_for, request, jsonify, make_response
from flask_wtf import FlaskForm
from flask import request
#from werkzeug import secure_filename
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import numpy as np
from flask_mail import Mail, Message
import MySQLdb
import flask_excel as excel
import pandas as pd
#import datetime as DT

# deadline_days = 7
# deadline = (DT.date.today() + DT.timedelta(days=deadline_days)).strftime('%d-%m-%y')

# Initialising the application
application = Flask(__name__)

#Excel
excel.init_excel(application)

@application.route("/upload", methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        global data
        # data = pd.DataFrame.from_dict(jsonify({"result": request.get_array(field_name='file')}))
        data =  request.get_array(field_name='file')
        details = pd.DataFrame(data)


# Initialise the Mail class object with application for sending emails
mail = Mail(application)

# Specifications for SQLAlchemy database
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
application.config['SECRET_KEY'] = 'secretkey123'     #Statutory for security reasons
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#application.config['UPLOAD_FOLDER'] = '/uploads_interviewbot/'
#application.config['MAX_CONTENT_PATH'] = '1000000'

"""

Two different databases are used:

1. SQLAlchemy: This is maintained locally to store the login credentials for the client users
2. MySQLdb: This is maintained in db4free.net to store the aspirant login email ID and topics for him/her

A different database is used for storing credential information locally for client privacy reasons.

"""

# Initialising SQLAlchemy database object for storing client login details
db = SQLAlchemy(application)

# Initialising hashing object for exchanging data between client and server
bcrypt = Bcrypt(application)

# Configuration for mail
application.config['MAIL_SERVER']='smtp.gmail.com'
application.config['MAIL_PORT'] = 465
application.config['MAIL_USERNAME'] = 'testing.interviewbot@gmail.com'
application.config['MAIL_PASSWORD'] = 'pass*123'
application.config['MAIL_USE_TLS'] = False
application.config['MAIL_USE_SSL'] = True
mail = Mail(application)

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

@application.before_first_request
def create_tables():

    """

    Create SQLAlchemy local database

    """

    db.create_all()

# Configuration for login manager which manages sessions
# Reference: https://flask-login.readthedocs.io/en/latest/
login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view="login"

@login_manager.user_loader
def load_user(user_id):

    """

    To retrieve users in sessions

    """

    return User.query.get(user_id)

# Instantiating the SQLAlchemy database for local storage of client credentials
db = SQLAlchemy()

class User(db.Model, UserMixin):
    
    """

    Objects of this 'User' class are the users. Also, these are the users whose data is stored in the SQLAlchemy database
    
    """

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class RegisterForm(FlaskForm):

    """

    This form is used for capturing registration details of client users.

    """

    username = StringField('username',validators=[InputRequired(), Length(min=0, max=20)])
    password = PasswordField('password',validators=[InputRequired(), Length(min=4, max=20)])
    submit = SubmitField("Sign up")

    def validate_username(self, username):

        """
        This function is used to ensure unique client users are allowed to register.

        """

        existing_user_username = User.query.filter_by(
            username = username.data).first()
        if existing_user_username:
            raise ValidationError(
                "That username already exists."
            )

class LoginForm(FlaskForm):

    """

    This form is used for capturing login details of client users.

    """

    username = StringField('username',validators=[InputRequired(), Length(min=0, max=20)])
    password = PasswordField('password',validators=[InputRequired(), Length(min=4, max=20)])
    submit = SubmitField("Log In")

@application.route("/")
def home():

    """

    This is the landing page for the client website

    """

    return render_template('home.html')

@application.route("/dashboard", methods=["GET","POST"])
@login_required
def dashboard():

    """

    This is the dashboard where the client user selects whether to generate interview(s) for single or multiple aspirants

    """

    return render_template('dashboard.html')

@application.route("/login", methods=["GET","POST"])
def login():

    """
    
    This is the login page for registered client users.
    
    Functionality:
    1. Instantiate the form and validate it
    2. Check if user is registered, if no, redirect to register page
    3. If user is registered and the hashed password matches LOG IN THE USER OBJECT
    4. Send the logged in user to the dashboard

    """

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
                login_user(user)
                return redirect(url_for("dashboard"))
        else:
            return redirect(url_for("register"))

    return render_template("login.html", form=form)

@application.route("/register", methods=["GET","POST"])
def register():

    """
    
    This is the register page for new client users.

    Functionality:
    1. Instantiate the form and validate it
    2. Hash the user entered password
    3. Create a new user OBJECT
    4. Add the new user OBJECT to the SQLAlchemy database
    5. Send the registered user to login page

    """

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

@application.route("/single_interview_generation", methods=["GET","POST"])
@login_required
def single_interview_generation():

    """
    
    This generates an interview for a single aspirant, stores the data in the database and sends an email

    Functionality:
    1. Get the topics to be tested from the form entered by the client user
    2. Join the topics, for storing in the MySQLdb database
    3. Get the email for the aspirant from the form entered by the client user
    4. Get the deadline for the interview from the form entered by the client user
    5. Send the 'email' of and the 'topics' for the aspirant to the MySQLdb database. This will be used by the aspirant side program.
    6. Draft the message for the aspirant
    7. Send the message to the aspirant
    7. Send the user to a success page

    """

    if request.method == "POST":
        #print("Inside here")
        test_topics = request.form.getlist("topic")
        topics_for_printing=", ".join(test_topics)
        emailt = request.form.get("email")
        #print(test_topics,"\n", emailt)
        #random_pass = np.random.randint(1000000000)
        deadline = request.form.get("deadline")
        r(f"INSERT into aspirant_topics(login,topics) VALUES ('{emailt}','{topics_for_printing}')")
        #Not to be sent. Ask user to register instead. Also can obtain user details like age etc.
        
        msg = Message(
                'Invitation for interview: Round 1 - Online interview',
                sender ='testing.interviewbot@gmail.com',
                recipients = [emailt]   #emailt
               )
        msg.body = f" Dear aspirant, \n\nCongratulations, you have been shortlisted for interview with 'The awesome data science company'. \nPlease take the interview at this link:_________________________. \nYou have to take the interview by {deadline}. \nYou will be tested in: {topics_for_printing}\n\nPlease login with this ID: {emailt}.\n\nWe wish you all the best! \nRegards,\nHR\nThe awesome data science company"
        mail.send(msg)
        
        return render_template('successt.html')
    return render_template("single_interview_generation.html")

def formatter(dataf):

    """
    
    This function accepts the dataframe for the multiple aspirants case and returns a list of emails and a dictionary of emails:[list of topics]
    
    Functionality:
    1. Replace blank entries by 'No'
    2. Replace 'Yes' in the topic columns by the topic name, i.e. 'Yes' in 'Statistics' -> 'Statistics'
       A demo is there in the test_pad.ipynb
    3. Store the list of emails
    4. Create the dictionary of {email:[list of topics]} for different aspirants
    5. Return the list of emails and the dictionary created above

    """
    dataf.fillna('No', inplace=True)
    for i in range(len(dataf)):
        for col in dataf.columns[1:]:
            dataf[col][i] = col if dataf[col][i]=='Yes' else ''
    emails = dataf.iloc[:,0].tolist()
    topics={}
    vals = {0:'Email',1:'Statistics',2:'Linear Regression',3:'Logistic Regression',4:'KNN',5:'SVM',6:'Kmeans',7:'Decision Tree',8:'Naive Bayes'}

    for i in range(dataf.shape[0]):
        topics[emails[i]]=[vals[kk] for kk in [x for x in dataf.iloc[i,:].tolist()[1:] if x!='']]
    emails = emails[1:]
    return emails, topics

@application.route("/multiple_interview_generation", methods=["GET","POST"])
@login_required
def multiple_interview_generation():
    """
    
    This generates interviews for multiple aspirants, stores the data in the database and sends emails

    Functionality:
    1. Provide sample csv file for upload
    2. Get the email and topics from the excel file to a dataframe for further processing
    3. Extract data from the dataset in the format of {emails:topics,..}
    4. Get the deadline for the interview from the form entered by the client user
    5. Send the 'email' of and the 'topics' for the aspirants to the MySQLdb database. This will be used by the aspirant side program.
    6. Draft the message for the aspirant
    7. Send the message to the aspirant
    7. Send the user to a success page

    """

    if request.method=="POST":

        deadline = request.form.get("deadline")
        data = pd.DataFrame(request.get_array(field_name='file'))
        emas, tpcs = formatter(data)
        # Not to be sent. Ask user to register instead. Also can obtain user details like age etc.
     
        for em in emas:
            # random_pass = np.random.randint(1000000000)    
            msg = Message(
                    'Invitation for interview: Round 1 - Online interview',
                    sender ='testing.interviewbot@gmail.com',
                    recipients = [em]   #emailt
                )
            msg.body = f" Dear aspirant, \n\nCongratulations, you have been shortlisted for interview with 'The awesome data science company'. \nPlease take the interview at this link:_________________________. \nYou have to take the interview by {deadline}. \nYou will be tested in: {', '.join(tpcs[em])}\n\nYour login credentials are: \n\nUsername: {em}.\n\nWe wish you all the best! \nRegards,\nHR\nThe awesome data science company"
            mail.send(msg)

            r(f"INSERT into aspirant_topics(login,topics) VALUES ('{em}','{', '.join(tpcs[em])}')")


        return render_template("successt.html")
    return render_template("multiple_interview_generation.html")

@application.route("/logout", methods=["GET","POST"])
@login_required
def logout():

    """

    To logout the user OBJECT and redirect to the landing page

    """
    
    logout_user()
    # user = current_user  #@@
    # user.authenticated = False  #@@
    # db.session.add(user)  #@@
    # db.session.commit()  #@@
    return redirect(url_for('home'))

if __name__=="__main__":

    """

    Controlling function

    """
    excel.init_excel(application)

    application.run(debug=True)

