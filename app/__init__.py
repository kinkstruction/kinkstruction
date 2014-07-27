from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from flask.ext.bcrypt import Bcrypt

from flask.ext.login import LoginManager

from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.config.from_object("config")
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

from app import views, models
