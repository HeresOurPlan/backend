from flask_cors import CORS
from flask import Flask

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@127.0.0.1:3306/heresourplan'
app.config['SECRET_KEY'] = 'heresourplansecret!'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

import heresourplan.routes.activity
import heresourplan.routes.authentication
import heresourplan.routes.profile
import heresourplan.routes.review

