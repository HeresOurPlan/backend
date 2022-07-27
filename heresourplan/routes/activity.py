import base64
import json

from . import object_as_dict

from ..entities import Activity
from ..entities import UserActivity
from ..entities import db
from .. import app

from flask import jsonify
from flask import request

import certifi
import ssl
import geopy.geocoders
from geopy.geocoders import Nominatim

def get_coord(address):
    ctx = ssl.create_default_context(cafile=certifi.where())
    geopy.geocoders.options.default_ssl_context = ctx
    geolocator = Nominatim(user_agent="my_request", scheme='http')
 
    #applying geocode method to get the location
    location = geolocator.geocode(address)
    print(address, location.latitude, location.longitude)
    return f"{location.latitude}, {location.longitude}"


@app.get("/activities")
def get_activities():
    activity_data = []
    activities = Activity.query.all()
    for activity in activities:
        parts = activity.locationCoord.split(",")
        lat = parts[0]
        lng = parts[1]
        activity_data.append({
            'activity_name': activity.activity_name,
            'address': activity.address,
            'opening_hours': activity.opening_hours,
            'closing_hours': activity.closing_hours,
            'lat': lat,
            'long': lng
            })
    return json.dumps(activity_data, indent=4, sort_keys=True, default=str)

@app.get("/useractivities/<username>")
def get_useractivities(username):
    useractivities = UserActivity.query.filter(
        UserActivity.username==username
    ).order_by(
        UserActivity.rank.asc() #order by rank
    ).all()
    res = [object_as_dict(Activity.query.get_or_404(useractivity.activity)) for useractivity in useractivities]
    for activity in res:
        assert activity is not None
        activity["img"] = base64.b64encode(activity["img"]).decode('utf-8')
        activity["opening_hours"] = str(activity["opening_hours"])
        activity["closing_hours"] = str(activity["closing_hours"])
        activity["img"] = f"data:{activity['mimetype']};base64,{activity['img']}"

    return jsonify(res)


@app.post('/activity') #adding individual activities
def add_activity():
    if request.json is None:
        raise Exception("No data submitted")
    new_activity = Activity(
        activity_name = request.json.get("activity_name"),
        address = request.json.get("address"),
        locationCoord = get_coord(request.json.get("address")),
        opening_hours = request.json.get("opening_hours"),
        closing_hours = request.json.get("closing_hours"),
        prior_booking = request.json.get("prior_booking"),
        website = request.json.get("website"),
        price_point = request.json.get("price_point"),
        category = request.json.get("category")
    )

    db.session.add(new_activity)
    db.session.commit()
    db.session.refresh(new_activity)

    new_activity = object_as_dict(new_activity)
    new_activity["opening_hours"] = str(new_activity["opening_hours"])
    new_activity["closing_hours"] = str(new_activity["closing_hours"])

    return jsonify(new_activity)

@app.post("/useractivities") #should it be post or put
def add_rank():
    if request.json is None:
        raise Exception("No data submitted")
    form_data = request.json
    useractivities = UserActivity.query.filter(
        UserActivity.username==form_data["username"]
    ).order_by(
        UserActivity.rank.asc()
    ).all()
    num_activities = len(useractivities)
    new_ranking = UserActivity(
        username = form_data["username"],
        activity = form_data["activity"],
        rank = num_activities + 1
    )
    db.session.add(new_ranking)
    db.session.commit()

    return "New Ranking Added!"

@app.delete("/activity/<activity_id>")
def activity_delete(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    db.session.delete(activity)
    db.session.commit()
    return "Activity Deleted!", 200

@app.put("/activity/<activity_id>") #editing existing individual activities - put = edit
def activity_upload(activity_id):
    if request.json is None:
        raise Exception("Request body is empty")
    print(activity_id)
    activity = Activity.query.get_or_404(activity_id)
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