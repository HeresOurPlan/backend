from flask import Flask, request, Response, render_template
from flask_sqlalchemy import SQLAlchemy
import pymysql
from app import Activity, User


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@127.0.0.1:3306/heresourplan'
app.config['SECRET_KEY'] = 'thisisasecretkey'

pymysql.install_as_MySQLdb()
db = SQLAlchemy(app)





