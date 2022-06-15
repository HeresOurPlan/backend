from ast import For
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
# from forms import RegistrationForm (i will uncomment this out later it keeps throwing error,,, TT –minnal)
# from wtforms import StringField, PasswordField, SubmitField
# from wtforms.validators import InputRequired, Length, ValidationError

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost:3306/heresourplan'
app.config['SECRET_KEY'] = 'thisisasecretkey'

pymysql.install_as_MySQLdb()
db = SQLAlchemy(app)


#engine = create_engine('mysql://root:root@localhost:3306/heresourplan')
#(((just ignore this bit for now tq -minnal)))


class User(db.Model, UserMixin):
    username = db.Column(db.String(20), nullable = False, unique = True, primary_key = True) #nullable=False -> whenever registering , field has to be entered in/cannot be empty;     #id = db.Column(db.Integer, primary_key = True)
    password = db.Column(db.String(80), nullable = False) #hashed pw is set to max 80 -- original pw is max 20
    name = db.Column(db.String(20), nullable = False)
    gender = db.Column(db.String(1), nullable = False)
    dob = db.Column(db.Date, nullable = False)
    email = db.Column(db.String(150), unique = True, nullable = False)
    contact = db.Column(db.String(8), nullable = False)
    #profile_url = db.Column(db.String(40), nullable=False,unique=True)
    #              (format assumed "heresourplans.com/u/username" so 20+20(username)), but tbh cant we j derive based on username?)

    user_activities = relationship("User_Activity")
    reviews = relationship("Review")
    visit_statuses = relationship("Visit_Status", back_populates="username")


class Activity(db.Model):
    postal = db.Column(db.String(6), nullable = False, primary_key = True)
    title = db.Column(db.String(80), nullable = False, primary_key=True)
    location = db.Column(db.String(80), nullable = False, primary_key = True)
    id = db.Column(db.Integer, nullable=False,unique=True)
    opening_hours = db.Column(db.Time, nullable = True)
    closing_hours = db.Column(db.Time, nullable = True)
    prior_booking = db.Column(db.Boolean, nullable = True)
    website = db.Column(db.String(80), nullable = True)
    price_point = db.Column(db.String(20), nullable = True)
    category = db.Column(db.String(20), nullable = False)

    reviews = relationship("Review")
    user_activities = relationship("User_Activity")
    visit_statuses = relationship("Visit_Status", back_populates="activity")
    similar_activities = relationship("Similar_Activity")

    ### if 1-many:    similar_activities = relationship("Similar_Activity") -- the current one
    ### if many-many: similar_activities = relationship("Similar_Activity",back_populates="sim_activity")
    ###               og_activity = relationship("Similar_Activity", back_populates="activity")
    ###               (or smth like that??? idk if need 2 separate statements or can combine in2 one...)

class User_Activity(db.Model):
    username = db.Column(db.String(20),ForeignKey("User.username"), nullable = False, primary_key = True)
    activity = db.Column(db.Integer, ForeignKey("Activity.id"), nullable = False, primary_key = True)
    rank = db.Column(db.Integer)

class Review(db.Model):
    username = db.Column(db.String(20), ForeignKey("User.username"), nullable = False, primary_key = True)
    activity = db.Column(db.Integer, ForeignKey("Activity.id"), nullable = False, primary_key = True)
    num_stars = db.Column(db.Integer, nullable = False)
    desc = db.Column(db.String(1000), nullable = True) #i put in a few nullable=True here n there so ppl dont hv to put in too much effort to make a complete record otherwize laze

class Similar_Activity(db.Model):
    activity = db.Column(db.Integer, ForeignKey("Activity.id"), nullable = False, primary_key = True)
    sim_activity = db.Column(db.Integer, ForeignKey("Activity.id"), nullable = False, primary_key = True)
    
    #https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#one-to-one
    #activity_relationship = relationship("Activity", backref("Activity.id", uselist = False)) #commented out cos idt it's 1-1, it's either 1-many or many-many

class Visit_Status(db.Model):
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
    if form_data.validate_on_submit():
        user = User.query.filter_by(username=form_data.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form_data.password.data):
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

    if form_data["username"] != db.session.username:
        hashed_password = bcrypt.generate_password_hash(form_data.password.data)
        new_user = User(
            username = form_data.username.data, 
            password = hashed_password,
            name = form_data.name.data,
            gender = form_data.gender.data,
            dob = form_data.dob.data,
            email = form_data.email.data,
            contact = form_data.contact.data
        )
        db.session.add(new_user)
        db.session.commit()
        return { "register_result": True }
    else:
        print("haha cannot register sucka")
        return { "register_result": False}


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

if __name__ == "__main__":
    app.run(debug=True) #running the app