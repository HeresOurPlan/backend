import pymysql

from . import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

pymysql.install_as_MySQLdb()
db = SQLAlchemy(app)


#engine = create_engine('mysql://root:root@localhost:3306/heresourplan')
#(((just ignore this bit for now tq -minnal)))


class User(db.Model):
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
    img = db.Column(db.LargeBinary(4000000))
    mimetype = db.Column(db.Text(255))


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
    activity_name = db.Column(db.String(80), nullable = False)
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


class VisitStatus(db.Model):
    __tablename__="VisitStatus"
    username = db.Column(db.String(20), ForeignKey("User.username"), nullable = False, primary_key = True)
    activity = db.Column(db.Integer, ForeignKey("Activity.id"), nullable = False, primary_key = True)
    has_visited = db.Column(db.Boolean, nullable = False)


db.create_all()