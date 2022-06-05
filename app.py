from ast import For
import pymysql
from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from sqlalchemy import ForeignKey
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost:3306/heresourplan'
app.config['SECRET_KEY'] = 'thisisasecretkey'

pymysql.install_as_MySQLdb()
db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    #id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), nullable = False, unique = True, primary_key = True) 
    #nullable=False -> whenever registering , field has to be entered in/cannot be empty
    password = db.Column(db.String(80), nullable = False)
    #hashed pw is set to max 80 -- original pw is max 20

    name = db.Column(db.String(20), nullable = False)
    gender = db.Column(db.String(1), nullable = False)
    dob = db.Column(db.Date, nullable = False)
    email = db.Column(db.String(20), unique = True, nullable = False)
    contact = db.Column(db.String(8), nullable = False)


class Activity(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    postal = db.Column(db.String(6), primary_key = True, nullable = False, unique = True)
    title = db.Column(db.String(80), nullable = False)
    location = db.Column(db.String(80), nullable = False)
    opening_hours = db.Column(db.Time, nullable = False)
    closing_hours = db.Column(db.Time, nullable = False)
    prior_booking = db.Column(db.Boolean, nullable = False)
    website = db.Column(db.String(80), nullable = False)
    price = db.Column(db.String(20), nullable = False)
    category = db.Column(db.String(20), nullable = False)

class User_Activity(db.Model, UserMixin):
    username = db.Column(ForeignKey("User.username"), nullable = False, unique = True, primary_key = True)
    activity = db.Column(ForeignKey("Activity.id"), nullable = False, unique = True, primary_key = True)
    rank = db.Column(db.Integer, unique = True)

class Review(db.Model, UserMixin):
    username = db.Column(ForeignKey("User.username"), nullable = False, unique = True, primary_key = True)
    activity = db.Column(ForeignKey("Activity.id"), nullable = False, unique = True, primary_key = True)
    num_stars = db.Column(db.Integer, nullable = False)
    desc = db.Column(db.String(120), nullable = False)

class Similar_Activity(db.Model, UserMixin):
    activity = db.Column(ForeignKey("Activity.id"), nullable = False, unique = True, primary_key = True)
    sim_activity = db.Column(ForeignKey("Activity.id"), nullable = False, unique = True, primary_key = True)
    #https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#one-to-one
    activity_relationship = relationship("Activity", backref("Activity.id", uselist = False))

class Visit_Status(db.Model, UserMixin):
    username = db.Column(ForeignKey("User.username"), nullable = False, unique = True, primary_key = True)
    activity = db.Column(ForeignKey("Activity.id"), nullable = False, unique = True, primary_key = True)
    has_visited = db.Column(db.Boolean, nullable = False)

db.create_all()

#in terminal -> from app import db
#imports db variable 
#db.create_all() -> create all the tables in the app file into db file
bcrypt = Bcrypt(app)


#mysql database.db -> in terminal -> checking whether changes are applied
#.tables -> checking each table
#.exit -> exit


login_manager = LoginManager() #allow app + flask to work tgt/loading users
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader #reload user ids stored in the session
def load_user(user_id):
    return User.query.get(int(user_id))



class RegisterForm(FlaskForm):
    username = StringField(validators = [InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators = [InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    name = StringField(validators = [InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Name"})
    gender = StringField(validators = [InputRequired(), Length(max = 1)], render_kw={"placeholder": "Gender (M/F)"})
    dob = StringField(validators = [InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Date of Birth"})
    email = StringField(validators = [InputRequired(), Length(min=10, max=80)], render_kw={"placeholder": "Email"})
    contact = StringField(validators = [InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Contact Number"})

    submit = SubmitField("Register")


    def validate_username(self, username):
        existing_username = User.query.filter_by(
            username=username.data).first()
        if existing_username:
            raise ValidationError("That username already exists. Please choose a different one.")


class LoginForm(FlaskForm):
    username = StringField(validators = [InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators = [InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")


@app.route("/") #all webpages go when loaded
def hello_world():
    return render_template("home.html")
#go to templates folder and search for file that is being passed in

@app.route("/dashboard",  methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first() #check if user in db
        if user: #if user in db
            if bcrypt.check_password_hash(user.password, form.password.data): #check user's pw and compare with form hashed pw
                login_user(user)
                return redirect(url_for("dashboard"))

    return render_template("login.html", form=form)


@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit(): #whenever form is validated - create a hashed pw
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(
            username = form.username.data, 
            password = hashed_password,
            name = form.name.data,
            gender = form.gender.data,
            dob = form.dob.data,
            email = form.email.data,
            contact = form.contact.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("register.html", form=form)

app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    app.run(debug=True) #running the app