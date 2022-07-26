import base64
import json

from . import object_as_dict
from ..entities import Activity
from ..entities import Review
from ..entities import db
from .. import app

from flask import jsonify
from flask import request


@app.get("/review/<username>/<activity_id>")
def get_review_activities(username, activity_id):
    reviews = Review.query.filter(
        Review.username==username
    ).order_by(
        Review.num_stars.desc() #order by num_stars
    ).all()
    res = [object_as_dict(Activity.query.get_or_404(review.activity)) for review in reviews]
    for activity in res:
        activity["img"] = base64.b64encode(activity["img"]).decode('utf-8')
        activity["opening_hours"] = str(activity["opening_hours"])
        activity["closing_hours"] = str(activity["closing_hours"])
        activity["img"] = f"data:{activity['mimetype']};base64,{activity['img']}"

    return jsonify(res)


@app.post("/reviews/<username>/<activity_id>")
def add_desc(username, activity_id):
    if request.json is None:
        raise Exception("No data submitted")
    input_star = request.json['num_stars']
    input_review = request.json['desc']

    new_review = Review(
        username = username,
        activity = activity_id,
        num_stars = input_star,
        desc = input_review
    )
    db.session.add(new_review)
    db.session.commit()

    return "New Review Added!"

@app.delete("/reviews/<username>/<activity_id>")
def review_delete(username, activity_id):
    review = Review.query.get_or_404(username).get_or_404(activity_id)
    db.session.delete(review)
    db.session.commit()
    return "Review Deleted!", 200
