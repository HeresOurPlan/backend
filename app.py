from ast import For
from importlib_metadata import email
import pymysql
from flask import Flask, jsonify, make_response, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine, inspect
from sqlalchemy.orm import backref, relationship, declarative_base
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from datetime import datetime
import jwt
import re
import json
import base64


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@127.0.0.1:3306/heresourplan'
app.config['SECRET_KEY'] = 'heresourplansecret!'

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
    img = db.Column(db.String(80), unique=True, nullable=True)
    mimetype = db.Column(db.String(80), nullable=True)
    imgfilename = db.Column(db.String(80), nullable=True)


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
    address = db.Column(db.String(80), nullable = False)
    locationCoord = db.Column(db.String(80), nullable = False)
    opening_hours = db.Column(db.Time, nullable = True)
    closing_hours = db.Column(db.Time, nullable = True)
    prior_booking = db.Column(db.String(1), nullable = True)
    website = db.Column(db.String(80), nullable = True)
    price_point = db.Column(db.String(20), nullable = True)
    category = db.Column(db.String(20), nullable = False)
    img = db.Column(db.LargeBinary(4000000))
    mimetype = db.Column(db.Text(255))

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
    username = form_data['username']
    password = form_data['password']
    user = User.query.filter_by(username=username).first()

    if not bcrypt.check_password_hash(user.password, password):
        return {"login_result": False}

    token = jwt.encode({"user": user.username}, "heresourplansekret")
    resp = make_response(jsonify({"login_result": True}))
    resp.headers["Authorization"] = token
    resp.headers["Access-Control-Expose-Headers"] = "Authorization"
    return resp

    # if form_data.validate_on_submit():
    #TODO:^ use this for querying database - change register

    # if user:
        # if bcrypt.check_password_hash(user.password, form_data['password']):
            # login_user(user)
            # return { "login_result": True }
    # return { "login_result": False }


    # if form_data["username"] == "bob":
    #     return { "login_result": False }
    # return { "login_result": True }


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


@app.get("/activities")
def get_activities():
    activity_data = []
    activities = Activity.query.all()
    for activity in activities:
        parts = activity.locationCoord.split(", ")
        lat = parts[0]
        lng = parts[1]
        activity_data.append({
            'title': activity.title,
            'coord': [lat, lng]
            })
    return json.dumps(activity_data, indent=4, sort_keys=True, default=str)

@app.get("/useractivities/<username>")
def get_useractivities(username):
    useractivities = UserActivity.query.filter(
        UserActivity.username==username
    ).order_by(
        UserActivity.rank.asc()
    ).all()
    res = [object_as_dict(Activity.query.get_or_404(useractivity.activity)) for useractivity in useractivities]
    for activity in res:
        activity["img"] = base64.b64encode(activity.get("img")).decode('utf-8')
        activity["opening_hours"] = str(activity["opening_hours"])
        activity["closing_hours"] = str(activity["closing_hours"])
        activity["img"] = f"data:{activity['mimetype']};base64,{activity['img']}"

    return jsonify(res)

def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


@app.get("/user")
def get_user():
    user = User.query.get(username) #how to get username for current session?
    return json.dumps(user, indent=4, sort_keys=True, default=str)


# @app.get("/useractivity")
# def joining_activity():
#     activity = Activity.query.all()
#     joining = Activity.query.join(
#         Activity, 
#         Activity.id==UserActivity.activity
#     ).add_columns(
#         Activity.id, 
#         Activity.img, 
#         Activity.mimetype, 
#         Activity.imgfilename, 
#         UserActivity.username, 
#         UserActivity.rank
#     ).all()
#     print(joining)
#     db.session.commit()

#     return "Activity Table Joined!"

@app.post('/activity') #adding individual activities
def add_activity():
    new_activity = Activity(
        postal = request.json.get("postal"),
        address = request.json.get("address"),
        locationCoord = request.json.get("locationCoord"),
        opening_hours = request.json.get("opening_hours"),
        closing_hours = request.json.get("closing_hours"),
        prior_booking = request.json.get("prior_booking"),
        website = request.json.get("website"),
        price_point = request.json.get("price_point"),
        category = request.json.get("category")
    )
    db.session.add(new_activity)
    db.session.commit()

    return "New Activity Added!"



@app.delete("/activity/<activity_id>")
def activity_delete(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    db.session.delete(activity)
    db.session.commit()
    return "Activity Deleted!", 200

@app.put("/activity/<activity_id>") #editing existing individual activities - put = edit
def activity_upload(activity_id):
    print(activity_id)
    activity = Activity.query.get_or_404(activity_id)
    activity.postal = request.json.get("postal")
    activity.address = request.json.get("address")
    activity.locationCoord = request.json.get("locationCoord")
    activity.opening = request.json.get("opening_hours")
    activity.closing = request.json.get("closing_hours")
    activity.prior = request.json.get("prior_booking")
    activity.website = request.json.get("website")
    activity.price = request.json.get("price_point")
    activity.category = request.json.get("category")

    db.session.commit()

    return 'Activity Updated!', 200

@app.put("/activity/image/<activity_id>") #inserting the image
def activity_image_upload(activity_id):
    print(activity_id)
    img = request.files.get("img")
    if not img:
        return 'No pic uploaded!', 400

    mimetype = img.mimetype
    if not mimetype:
        return 'Bad upload!', 400

    activity = Activity.query.get_or_404(activity_id)
    activity.img = img.read()
    activity.mimetype = mimetype

    db.session.commit()

    return 'Activity Img Uploaded!', 200


# def act_decode_img(img):
#     return base64.b64encode.decode('utf-8')



@app.put('/profileEdit/<username>')
def edit_profile(username):
    user = User.query.get_or_404(username)
    user.password = request.json.get("password") #can just change password like this?
    user.name = request.json.get("name")
    user.gender = request.json.get("gender")
    user.dob = request.json.get("dob")
    user.email = request.json.get("email")
    user.contact = request.json.get("contact")

    db.session.commit()

    return 'Profile Updated!', 200


# def joining_tables_profile():
#     user = User.query.all()
#     User.query.join(User, user.id==UserActivity.username).add_columns(User.id, User.img, User.mimetype, User.imgfilename, UserActivity.activity_id, UserActivity.rank)

#     db.session.commit()

#     return "user table joined!"

@app.put("/profileEdit/image/<username>") 
def profile_upload(username):
    img = request.files.get("img")
    if not img:
        return 'No pic uploaded!', 400

    mimetype = img.mimetype
    if not mimetype:
        return 'Bad upload!', 400

    user = User.query.get_or_404(username) 
    user.img = img.read()
    user.mimetype = mimetype

    db.session.commit()

    return 'Profile Pic Uploaded!', 200

# def profile_convert_to_base_to_img():
#     user_img = request.form["img"]
#     with open(user_img, "rb") as img_file:
#         encoded_string = base64.b64encode(img_file.read())
    
    # return encoded_string.decode('utf-8')


@app.put("/profileEdit/password/<username>") 
def password_change(username):
    new_password = request.json("password")
    cfm_password = request.json("confirm_password")
    if new_password != cfm_password:
        return "Passwords do not match", 200
    hashed_password = bcrypt.generate_password_hash(new_password)

    user.password = hashed_password
    db.session.commit()

    return "Password Changed", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True) #running the app

