from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bcrypt import Bcrypt
from flask.ext.mail import Mail
from flask.ext.login import LoginManager
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from mailer import VerificationMailer, ResetPasswordMailer
from flaskext.markdown import Markdown


app = Flask(__name__)
app.config.from_object("config")
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
verificationMailer = VerificationMailer(app, mail)
passwordMailer = ResetPasswordMailer(app, mail)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

Markdown(app)

if app.config.get('DEBUG'):
    app.config['SERVER_NAME'] = "localhost:8000"
else:
    app.config['SERVER_NAME'] = 'kinkstruction.com'

# for key in sorted(app.config.keys()):
#     print key + ": " + str(app.config.get(key))

from app import views, models, verificationMailer, passwordMailer, mail
