from ast import For
from importlib_metadata import email
import pymysql
from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import backref, relationship, declarative_base
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from datetime import datetime
import re
import json
# from forms import RegistrationForm (i will uncomment this out later it keeps throwing error,,, TT –minnal)
# from wtforms import StringField, PasswordField, SubmitField
# from wtforms.validators import InputRequired, Length, ValidationError

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@127.0.0.1:3306/heresourplan'
app.config['SECRET_KEY'] = 'thisisasecretkey'

pymysql.install_as_MySQLdb()
db = SQLAlchemy(app)


#engine = create_engine('mysql://root:root@localhost:3306/heresourplan')
#(((just ignore this bit for now tq -minnal)))


class User(db.Model, UserMixin):
    __tablename__="User"
    username = db.Column(db.String(20), nullable = False, unique = True, primary_key = True) #nullable=False -> whenever registering , field has to be entered in/cannot be empty;     #id = db.Column(db.Integer, primary_key = True)
    password = db.Column(db.String(80), nullable = False) #hashed pw is set to max 80 -- original pw is max 20
    name = db.Column(db.String(20), nullable = False)
    gender = db.Column(db.String(1), nullable = False)
    dob = db.Column(db.Date, nullable = False)
    email = db.Column(db.String(150), unique = True, nullable = False)
    contact = db.Column(db.String(8), nullable = False)
    #profile_url = db.Column(db.String(40), nullable=False,unique=True)
    #              (format assumed "heresourplans.com/u/username" so 20+20(username)), but tbh cant we j derive based on username?)

    user_activities = relationship("UserActivity")
    reviews = relationship("Review")
    visit_statuses = relationship("VisitStatus", backref="User_ref")
    def get_id(self):
            return (self.username)

SimilarActivity = db.Table(
    "SimilarActivity",
    db.Column("activity_id", db.Integer, db.ForeignKey("Activity.id")),
    db.Column("other_activity_id", db.Integer, db.ForeignKey("Activity.id")),
)

    

class Activity(db.Model):
    __tablename__="Activity"
    id = db.Column(db.Integer, nullable=False,unique=True, primary_key=True)
    postal = db.Column(db.String(6), nullable = False)
    title = db.Column(db.String(80), nullable = False)
    location = db.Column(db.String(80), nullable = False)
    opening_hours = db.Column(db.Time, nullable = True)
    closing_hours = db.Column(db.Time, nullable = True)
    prior_booking = db.Column(db.Boolean, nullable = True)
    website = db.Column(db.String(80), nullable = True)
    price_point = db.Column(db.String(20), nullable = True)
    category = db.Column(db.String(20), nullable = False)
    img = db.Column(db.String(80), unique=True, nullable=False)
    mimetype = db.Column(db.String(80), nullable=False)
    imgfilename = db.Column(db.String(80), nullable=False)

    reviews = db.relationship("Review")
    user_activities = db.relationship("UserActivity")
    visit_statuses = db.relationship("VisitStatus", backref="activity_ref")
    # similar_activities = relationship("SimilarActivity")
    similar_activities = db.relationship(
        "Activity", 
        secondary="SimilarActivity",
        primaryjoin="SimilarActivity.c.activity_id==Activity.id",
        secondaryjoin="SimilarActivity.c.other_activity_id==Activity.id",
        backref="sim_activity"
    )


    ### if 1-many:    similar_activities = relationship("Similar_Activity") -- the current one
    ### if many-many: similar_activities = relationship("Similar_Activity",back_populates="sim_activity")
    ###               og_activity = relationship("Similar_Activity", back_populates="activity")
    ###               (or smth like that??? idk if need 2 separate statements or can combine in2 one...)

class UserActivity(db.Model):
    __tablename__="UserActivity"
    username = db.Column(db.String(20),ForeignKey("User.username"), nullable = False, primary_key = True)
    activity = db.Column(db.Integer, ForeignKey("Activity.id"), nullable = False, primary_key = True)
    img = db.Column(db.String(80),ForeignKey("Activity.img"), nullable = False)
    imgfilename = db.Column(db.String(80),ForeignKey("Activity.filename"), nullable = False)
    rank = db.Column(db.Integer)

class Review(db.Model):
    __tablename__="Review"
    username = db.Column(db.String(20), ForeignKey("User.username"), nullable = False, primary_key = True)
    activity = db.Column(db.Integer, ForeignKey("Activity.id"), nullable = False, primary_key = True)
    num_stars = db.Column(db.Integer, nullable = False)
    desc = db.Column(db.String(1000), nullable = True) #i put in a few nullable=True here n there so ppl dont hv to put in too much effort to make a complete record otherwize laze


    
    #https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#one-to-one
    #activity_relationship = relationship("Activity", backref("Activity.id", uselist = False)) #commented out cos idt it's 1-1, it's either 1-many or many-many

class VisitStatus(db.Model):
    __tablename__="VisitStatus"
    username = db.Column(db.String(20), ForeignKey("User.username"), nullable = False, primary_key = True)
    activity = db.Column(db.Integer, ForeignKey("Activity.id"), nullable = False, primary_key = True)
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


# class RegisterForm(FlaskForm):
#     username = StringField(validators = [InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
#     password = PasswordField(validators = [InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
#     name = StringField(validators = [InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Name"})
#     gender = StringField(validators = [InputRequired(), Length(max = 1)], render_kw={"placeholder": "Gender (M/F)"})
#     dob = StringField(validators = [InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Date of Birth"})
#     email = StringField(validators = [InputRequired(), Length(min=10, max=80)], render_kw={"placeholder": "Email"})
#     contact = StringField(validators = [InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Contact Number"})

#     submit = SubmitField("Register")


    # def validate_username(self, username):
    #     existing_username = User.query.filter_by(
    #         username=username.data).first()
    #     if existing_username:
    #         raise ValidationError("That username already exists. Please choose a different one.")


# class LoginForm(FlaskForm):
#     username = StringField(validators = [InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
#     password = PasswordField(validators = [InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
#     submit = SubmitField("Login")


@app.route("/") #all webpages go when loaded
def hello_world():
    return render_template("home.html")
#go to templates folder and search for file that is being passed in

@app.route("/dashboard",  methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/login", methods=['POST'])
def login():
    form_data = request.json
    print(form_data)
    # if form_data.validate_on_submit():
    user = User.query.filter_by(username=form_data['username']).first()
    #TODO:^ use this for querying database - change register
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
    if user:
        if bcrypt.check_password_hash(user.password, form_data['password']):
            login_user(user)
            return { "login_result": True }
    return { "login_result": False }


    # if form_data["username"] == "bob":
    #     return { "login_result": False }
    # return { "login_result": True }


    # form = LoginForm()
    # if form.validate_on_submit():
    #     user = User.query.filter_by(username=form.username.data).first() #check if user in db
    #     if user: #if user in db
    #         if bcrypt.check_password_hash(user.password, form.password.data): #check user's pw and compare with form hashed pw
    #             login_user(user)
    #             return redirect(url_for("dashboard"))

    # return render_template("login.html", form=form)

@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/register", methods=['POST'])
def register():
    form_data = request.json
    print(form_data)
    if form_data['password'] != form_data['confirm_password']:
        print('wrong pass')
        return { 'registration_result': 'wrongpassword' }
    if re.match("[a-z0-9]+@[a-z]+\.[a-z]{2,3}", form_data['email']) == None:
        return { 'registration_result': 'invalidemail' }
    
    user_db = User.query.filter_by(username=form_data['username']).first()
    email_db = User.query.filter_by(email=form_data['email']).first()
    if user_db:
        return { 'registration_result': 'usernametaken'}
    if email_db:
        return { 'registration_result': 'emailtaken'}

    # cur = pymysql.connection.cursor()
    # username_statement = "SELECT * FROM User WHERE username = %s"
    # x = cur.execute(username_statement, form_data['username'])
    # if int(x)>0:
    #     return { 'registration_result': 'usernametaken' }
    # email_statement = "SELECT * FROM User WHERE email = %s"
    # y = cur.execute(email_statement, form_data['email'])
    # if int(y)>0:
    #     return { 'registration_result': 'emailtaken' }



    hashed_password = bcrypt.generate_password_hash(form_data['password'])
    new_user = User(
        username = form_data['username'], 
        password = hashed_password,
        name = form_data['name'],
        gender = form_data['gender'],
        dob = form_data['dob'],
        email = form_data['email'],
        contact = form_data['contact']
    )
    db.session.add(new_user)
    db.session.commit()
    return { "registration_result": True }
    # else:
    #     print("haha cannot register sucka")
    #     return { "register_result": False}


    # if form.validate_on_submit(): #whenever form is validated - create a hashed pw
    #     hashed_password = bcrypt.generate_password_hash(form.password.data)
    #     new_user = User(
    #         username = form.username.data, 
    #         password = hashed_password,
    #         name = form.name.data,
    #         gender = form.gender.data,
    #         dob = form.dob.data,
    #         email = form.email.data,
    #         contact = form.contact.data)
    #     db.session.add(new_user)
    #     db.session.commit()
    #     return redirect(url_for("login"))

    # return render_template("register.html", form=form)

app.run(host="0.0.0.0", port=8080)

@app.get("/activities")
def get_activities():
    activity_data = []
    activities = Activity.query.all()
    for activity in activities:
        parts = activity.location.split(", ")
        lat = parts[0]
        lng = parts[1]
        activity_data.append({
            'title': activity.title,
            'coord': [lat, lng]
            })
    return json.dumps(activity_data, indent=4, sort_keys=True, default=str)

@app.get("/useractivities")
def get_useractivities():
    useractivities = UserActivity.query.all()
    ranking = []
    user = User.query.get(username) #how to get username for current session?
    if user == useractivities.username:
        for indiv in useractivities:
            ranking.append({
                'rank': [indiv.filename, indiv.activity]
            })
    return json.dumps(useractivities, indent=4, sort_keys=True, default=str)



if __name__ == "__main__":
    app.run(debug=True) #running the app

