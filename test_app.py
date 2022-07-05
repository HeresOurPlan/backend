from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy import insert, delete, update
from sqlalchemy.orm import backref, relationship, declarative_base

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost:3306/heresourplan'
app.config['SECRET_KEY'] = 'thisisasecretkey'

pymysql.install_as_MySQLdb()
db = SQLAlchemy(app)

#HELP HOW DO I OPEN THE EXISTING DATABASE i hope its correct

db.User.insert().values({"username": "keithlaw",
                         "password": "password",
                         "name": "Keith Law",
                         "gender": "M",
                         "dob": "30/05/1999",
                         "email": "keithlaw@gmail.com",
                         "contact": "62353535"
                    })
                    #this one will test for usernametaken, emailtaken, wrongpassword
#test invalid email separately