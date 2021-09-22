from flask import Flask, redirect, render_template, url_for, request
from flask_wtf import FlaskForm
#from werkzeug import secure_filename
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import numpy as np
from flask_mail import Mail, Message

app = Flask(__name__)
mail = Mail(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secretkey123'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['UPLOAD_FOLDER'] = '/uploads_interviewbot/'
#app.config['MAX_CONTENT_PATH'] = '1000000'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# configuration of mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'testing.interviewbot@gmail.com'
app.config['MAIL_PASSWORD'] = 'pass*123'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

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
    username = StringField('username',validators=[InputRequired(), Length(min=0, max=20)])
    password = PasswordField('password',validators=[InputRequired(), Length(min=4, max=20)])
    submit = SubmitField("Sign up")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username = username.data).first()
        if existing_user_username:
            raise ValidationError(
                "That username already exists."
            )

class LoginForm(FlaskForm):
    username = StringField('username',validators=[InputRequired(), Length(min=0, max=20)])
    password = PasswordField('password',validators=[InputRequired(), Length(min=4, max=20)])
    submit = SubmitField("Log In")

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/dashboard", methods=["GET","POST"])
@login_required
def dashboard():
    return render_template('dashboard.html')

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

@app.route("/single_interview_generation", methods=["GET","POST"])
@login_required
def single_interview_generation():
    if request.method == "POST":
        #print("Inside here")
        test_topics = request.form.getlist("topic")
        topics_for_printing=", ".join(test_topics)
        emailt = request.form.get("email")
        print(test_topics,"\n", emailt)
        random_pass = np.random.randint(1000000000)
        deadline = request.form.get("deadline")

        #Not to be sent. Ask user to register instead. Also can obtain user details like age etc.
        #Also send email data to SQLdb and check at client side later
        
        msg = Message(
                'Invitation for interview: Round 1 - Online interview',
                sender ='testing.interviewbot@gmail.com',
                recipients = [emailt]   #emailt
               )
        msg.body = f" Dear aspirant, \n\nCongratulations, you have been shortlisted for interview with 'The awesome data science company'. \nPlease take the interview at this link:_________________________. \nYou have to take the interview by {deadline}. \nYou will be tested in: {topics_for_printing}\n\nYour login credentials are: \n\nUsername: {emailt}\nPassword: {random_pass}.\n\nWe wish you all the best! \nRegards,\nHR\nThe awesome data science company"
        mail.send(msg)
        return render_template('successt.html')
    return render_template("single_interview_generation.html")

def formatter(dataf):
    dataf.fillna('No', inplace=True)
    for i in range(len(dataf)):
        for col in dataf.columns[1:]:
            dataf[col][i] = col if dataf[col][i]=='Yes' else ''
    emails = dataf.Email.tolist()
    topics={}
    for i in range(dataf.shape[0]):
        topics[emails[i]]=[x for x in dataf.iloc[i].tolist()[1:] if x!='']
    return emails, topics

@app.route("/multiple_interview_generation", methods=["GET","POST"])
@login_required
def multiple_interview_generation():
    
    if request.method=="POST":
        
        
        #uploaded_excel = request.form.get("file")
        #print("Excel uploaded")
        #uploaded_excel.save(secure_filename(uploaded_excel.filename))
        
        
        
        # a dataframe has to be sent
        emas, tpcs = formatter(uploaded_excel)
        #Not to be sent. Ask user to register instead. Also can obtain user details like age etc.
        #Also send email data to SQLdb and check at client side later
        
        for em in emas:  
            random_pass = np.random.randint(1000000000)    
            msg = Message(
                    'Invitation for interview: Round 1 - Online interview',
                    sender ='testing.interviewbot@gmail.com',
                    recipients = [em]   #emailt
                )

            msg.body = f" Dear aspirant, \n\nCongratulations, you have been shortlisted for interview with 'The awesome data science company'. \nPlease take the interview at this link:_________________________. \nYou have to take the interview by {deadline}. \nYou will be tested in: {tpcs[em]}\n\nYour login credentials are: \n\nUsername: {em}\nPassword: {random_pass}.\n\nWe wish you all the best! \nRegards,\nHR\nThe awesome data science company"
            mail.send(msg)

        return render_template("successt.html")
    return render_template("multiple_interview_generation.html")

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

