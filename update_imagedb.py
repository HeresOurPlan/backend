from flask import Flask, request, Response, render_template
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import pymysql
from app import Activity, User


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@127.0.0.1:3306/heresourplan'
app.config['SECRET_KEY'] = 'thisisasecretkey'

pymysql.install_as_MySQLdb()
db = SQLAlchemy(app)



@app.route("/") #all webpages go when loaded
def hello_world():
    return render_template("home.html")

@app.route('/addactivity/image', methods=['GET', 'POST'])
def upload():
    activity = Activity.query.get_or_404(id=id) #how do i get activity id here
    pic = activity['pic'] #'pic' is the name of the key in frontend
    if not pic:
        return 'No pic uploaded!', 400


    filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    if not filename or not mimetype:
        return 'Bad upload!', 400

    activity = Activity.query.get_or_404(id=id) #how do i get activity id here
    activity.img = pic.read()
    activity.mimetype = mimetype
    activity.imgfilename = filename

    db.session.commit()

    return 'Img Uploaded!', 200


@app.route('/profileEdit/image', methods=['GET', 'POST'])
def upload():
    user = User.query.get_or_404(id=id) #how do i get activity id here
    pic = user['pic'] #'pic' is the name of the key in frontend
    if not pic:
        return 'No pic uploaded!', 400


    filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    if not filename or not mimetype:
        return 'Bad upload!', 400

    user = User.query.get_or_404(id=id) #how do i get activity id here
    user.mimetype = mimetype
    user.img = pic.read()
    user.imgfilename = filename

    db.session.commit()

    return 'Img Uploaded!', 200


