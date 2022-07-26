from flask import request

from ..entities import User
from ..entities import db
from .. import app

@app.put('/profileEdit/<username>')
def edit_profile(username):
    if request.json is None:
        raise Exception("No data is submitted")
    user = User.query.get_or_404(username)
    user.password = request.json.get("password") #can just change password like this?
    user.name = request.json.get("name")
    user.gender = request.json.get("gender")
    user.dob = request.json.get("dob")
    user.email = request.json.get("email")
    user.contact = request.json.get("contact")
    db.session.commit()
    return 'Profile Updated!', 200

@app.put("/profileEdit/image/<username>")
def profile_upload(username):
    img = request.files.get("img")
    if not img:
        return "No pic uploaded!", 400

    mimetype = img.mimetype
    if not mimetype:
        return "Bad upload!", 400

    user = User.query.get_or_404(username)
    user.img = img.read()
    user.mimetype = mimetype

    db.session.commit()

    return "Profile Pic Uploaded!", 200


