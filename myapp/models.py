from myapp import db
from flask_login import UserMixin

class History(db.Model):
    __tablename__ = 'history' 
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(500), nullable=False)
    ctime= db.Column(db.BigInteger, nullable=False) # each message send time used for extract message
    sender = db.Column(db.String(120), nullable=False)
    receiver = db.Column(db.String(120), nullable=False)
    read_status = db.Column(db.Boolean, nullable=False)
    def __init__(self, message, ctime, sender, receiver, read_status = False):
        self.message = message
        self.ctime = ctime
        self.sender = sender
        self.receiver = receiver
        self.read_status = read_status
    def __repr__(self):
        return '<History chat from: {0}, to: {1}, with message: {2}>'.format(self.sender, self.receiver, self.message)

class User(UserMixin, db.Model):
    __tablename__= 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hashed = db.Column(db.String, nullable=False)
    confirm_email = db.Column(db.Boolean, nullable=False)
    def __init__(self, username, email, hashed, confirm_email):
        self.username = username
        self.email = email
        self.hashed = hashed
        self.confirm_email = confirm_email
    def __repr__(self):
        return '<User %r>' % self.username

class Schedule(db.Model):
    __tablename__='schedules'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    startdate = db.Column(db.String, nullable=False)
    origination = db.Column(db.String, nullable=False)
    destination = db.Column(db.String, nullable=False)
    leaving_city = db.Column(db.String, nullable=False)
    arriving_city = db.Column(db.String, nullable=False)
    flightnumber = db.Column(db.String, nullable=False)
    def __init__(self, username, startdate, origination, destination, leaving_city, arriving_city,flightnumber):
        self.username = username
        self.startdate = startdate
        self.origination = origination
        self.destination = destination
        self.leaving_city = leaving_city
        self.arriving_city = arriving_city
        self.flightnumber = flightnumber
    def __repr__(self):
        return '<Schedule for user: {}.'.format(self.username)

class Flyreq(db.Model):
    __tablename__ = 'flyreqs'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    leaving_city = db.Column(db.String, nullable=False)
    arriving_city = db.Column(db.String, nullable=False)
    flightnumber = db.Column(db.String, nullable=True)
    requesttext = db.Column(db.Text, nullable=False)
    moneyamount = db.Column(db.String, nullable=False)
    event_date = db.Column(db.String, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    def __init__(self, username, event_date, leaving_city, arriving_city,flightnumber, requesttext, moneyamount, email):
        self.username = username
        self.event_date = event_date
        self.leaving_city = leaving_city
        self.arriving_city = arriving_city
        self.flightnumber = flightnumber
        self.requesttext = requesttext
        self.moneyamount = moneyamount
        self.email= email
    def __repr__(self):
        return '<Flyreq obj for user: {}.>'.format(self.username)

class Airport(db.Model):
    __tablename__='airports'
    airport_id = db.Column(db.Integer, primary_key=True)
    airport_name = db.Column(db.String, nullable=False)
    city = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False)
    IATA = db.Column(db.String, nullable=True)
    ICAO = db.Column(db.String, nullable=True)
    latitude = db.Column(db.Numeric, nullable=True)
    longitude = db.Column(db.Numeric, nullable=True)
    altitude = db.Column(db.Numeric, nullable=True)
    timezone = db.Column(db.Numeric, nullable=True)
    DST = db.Column(db.String, nullable=True)
    TZ = db.Column(db.String, nullable=True)
    obj_type = db.Column(db.String, nullable=True)
    data_source = db.Column(db.String, nullable=True)
    def __init__(self, airport_name, city, country, IATA, ICAO, latitude, longitude, altitude, timezone, DST, TZ, obj_type, data_source):
        self.airport_name = airport_name
        self.city = city
        self.country = country
        self.iata = IATA
        self.icao = ICAO
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.timezone = timezone
        self.dst = DST
        self.tz = TZ
        self.obj_type = obj_type
        self.data_source = data_source
    def __repr__(self):
        return '<This is an Airport object, name: %r>' % self.airport_name
