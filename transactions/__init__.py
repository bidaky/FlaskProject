from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt

app = Flask(__name__, template_folder='templates')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:pgnulp@127.0.0.1/bidaky'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Lab9'


db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)