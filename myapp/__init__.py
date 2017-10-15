"""
#IMPORTING flask.ext.uploads IS DEPRECATED, USE flask_uploads INSTEAD
"""
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
from flask_mail import Mail
from flask_jsglue import JSGlue
from flask_login import LoginManager
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO
from flask_heroku import Heroku
from itsdangerous import URLSafeTimedSerializer
from . import configmodule
import os

app = Flask(__name__)
app.config.from_object(configmodule.Config)
app.config['DEBUG'] = False

db = SQLAlchemy(app)
babel = Babel(app)
mail = Mail(app)
jsglue = JSGlue(app)
login_manager = LoginManager()
login_manager.init_app(app)
photos = UploadSet('photos', IMAGES)
heroku = Heroku(app)
socketio = SocketIO(app)
s = URLSafeTimedSerializer(os.environ['SECRET_KEY'])

"""
#CONFIGURE SESSION TO USE FILESYSTEM INSTEAD OF SIGNED COOKIES
#INSTANTIATE FLASK-BOOTSTRAP
#CONFIGURE IMURG PIC UPLOADS
"""
Session(app)
Bootstrap(app)
configure_uploads(app, photos)

from myapp import views, models
