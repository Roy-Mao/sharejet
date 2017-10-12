import os
from tempfile import mkdtemp
#THE ENVIRONMENT CONFIGURATION FOR MY SHAREJET APP
class Config(object):
	SECRET_KEY = os.environ['SECRET_KEY']
	SESSION_FILE_DIR = mkdtemp()
	SESSION_PERMANENT = False
	SESSION_TYPE = "filesystem"
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	BABEL_DEFAULT_LOCALE = "en"
	BABEL_DEFAULT_TIMEZONE = "UTC"
	MAIL_SERVER = "smtp.mail.yahoo.com"
	MAIL_USERNAME = "lee.rio@yahoo.com"
	MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
	MAIL_PORT = 465
	MAIL_USE_SSL = True
	MAIL_USE_TLS = False
	USE_SESSION_FOR_NEXT= True
	UPLOADED_PHOTOS_DEST = 'static/img'
	TESTING = False
	SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
	DEBUG = os.environ['DEBUG_MOD']
