from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from fordatabase import db

app = Flask(__name__)



app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/wh'
app.config['SECRET_KEY'] = "1234:)"
app.config['UPLOAD_FOLDER'] = '/static/img/'
db.init_app(app)



