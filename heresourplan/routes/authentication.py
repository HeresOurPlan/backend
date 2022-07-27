import json
import jwt
import re

from ..entities import User
from ..entities import db
from .. import app

from flask import jsonify
from flask import make_response
from flask import request
from flask import session
from flask_bcrypt import Bcrypt


bcrypt = Bcrypt(app)

@app.get("/user/<username>")
def get_user(username):
    # print(session)
    # user_id = session['username']
    user = User.query.filter_by(username=username).first()
    user_data = ({
        'username': user.username,
        'name': user.name,
        'gender': user.gender,
        'dob': user.dob,
        'email': user.email,
        'contact': user.contact
        })
    return json.dumps(user_data, indent=4, sort_keys=True, default=str)

    user = User.query.get(username) #how to get username for current session?
    return json.dumps(user, indent=4, sort_keys=True, default=str)


@app.route("/login", methods=['POST'])
def login():
    form_data = request.json
    if form_data is None:
        raise Exception("Form data is none")

    print(form_data)
    username = form_data['username']
    session['username'] = form_data['username']
    password = form_data['password']
    user = User.query.filter_by(username=username).first()

    if not bcrypt.check_password_hash(user.password, password):
        return {"login_result": False}

    token = jwt.encode({"user": user.username}, "heresourplansekret")
    resp = make_response(jsonify({"login_result": True}))
    resp.headers["Authorization"] = str(token)
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


@app.route("/register", methods=['POST'])
def register():

    form_data = request.json
    if form_data is None:
        raise Exception("Form data is none")

    if form_data['password'] != form_data['confirm_password']:
        print('wrong pass')
        return { 'registration_result': 'wrongpassword' }
    if re.match(r"[a-z0-9]+@[a-z]+\.[a-z]{2,3}", form_data['email']) == None:
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

# TODO: Change password does not work, it aint even getting the user
@app.put("/profileEdit/password/<username>")
def password_change(username):
    if request.json is None:
        raise Exception("Request body is missing")

    new_password = request.json.get("password")
    cfm_password = request.json.get("confirm_password")
    if new_password != cfm_password:
        return "Passwords do not match", 200

    hashed_password = bcrypt.generate_password_hash(new_password)

    User.password = hashed_password
    db.session.commit()

    return "Password Changed", 200
