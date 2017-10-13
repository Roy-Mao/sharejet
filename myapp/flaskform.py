#Form ALREADY DEPRECATED SINCE VERSION 0.13: RENAMED TO FlaskForm
#FROM VERSION 0.9.0, FLASK-WTF WILL NOT IMPORT ANYTHING FROM WTFORMS,NEED TO IMPORT FIELDS FROM WTFORMS
#TextField HAS BEEN DEPRECATED IN WTForms SO StringField SHOULD BE USED INSTEAD
from flask import request
from flask_wtf import FlaskForm
from passlib.apps import custom_app_context as pwd_context
from wtforms.validators import InputRequired, Email, Length, EqualTo, ValidationError, Regexp
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField, SubmitField
from .models import History, User, Schedule, Flyreq, Airport



class LoginForm(FlaskForm):
    email = StringField('Email', validators = [InputRequired('Email address is required!'), Email("Invalid Email Address")])
    password = PasswordField('Password', validators = [InputRequired('Password is required!'), Length(min=5, max=15, message="Must between 5 and 15 characters!")])
    remember = BooleanField('Remember me')
    def validate_email(self, field):
        this_user = User.query.filter_by(email=field.data).first()
        if this_user is None:
            raise ValidationError('This email has not been registered yet.')
        if not this_user.confirm_email:
            raise ValidationError('You might forget to activate your account. Please verify it through the email link.')
    def validate_password(self, field):
        user_email = request.form.get('email')
        this_user = User.query.filter_by(email=user_email).first()
        if this_user is not None:
            user_pw = this_user.hashed
            if not pwd_context.verify(request.form.get('password'), user_pw):
                raise ValidationError('Username and password does not match.')

class RegistrationForm(FlaskForm):
    username = StringField('Username',validators=[InputRequired('A username is required!'), Length(min=3, max=10, message="Must between 3 and 10 characters!"), Regexp('^\w+$', message="Only letters, numbers and underscores are allowed.")])
    email = StringField('Email', validators = [InputRequired('Email address is required!'), Length(min=6, message="Your email address is too short!"), Email("Invalid Email Address")])
    password = PasswordField('Password', validators = [InputRequired('Password is required!'), Length(min=5, max=15, message="Must between 5 and 15 characters!"), EqualTo('c_password', message='Reconfirm your password again.')])
    c_password = PasswordField('Repeat your password')
    # In-line Validators, by defining a method with the convention validate_fieldname
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already existed.')
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('This email has already been registered.')

class ResetpasswordForm(FlaskForm):
    oldpassword = PasswordField('Old Password', validators = [InputRequired('Password is required!'), Length(min=5, max=15, message="Must between 5 and 15 characters!")])
    newpassword = PasswordField('New Password', validators = [InputRequired('Password is required!'), Length(min=5, max=15, message="Must between 5 and 15 characters!")])
    conpassword = PasswordField('Confirm', validators = [InputRequired('Password is required!'), Length(min=5, max=15, message="Must between 5 and 15 characters!"), EqualTo('newpassword', message='Reconfirm your new password again.')])
    def validate_oldpassword(self, field):
        user_id = session['user_id']
        this_user = User.query.filter_by(id=user_id).first()
        user_hash = this_user.hashed
        old_pw = request.form.get('oldpassword')
        match_old = pwd_context.verify(old_pw, user_hash)
        if not match_old:
            raise ValidationError('Wrong old password, Try again.')
    def validate_newpassword(self, field):
        new_pw = request.form.get('newpassword')
        old_pw = request.form.get('oldpassword')
        if new_pw == old_pw:
            raise ValidationError('New password should not be the same as the old one.')

class SearchForm(FlaskForm):
    startdate = StringField('Date', validators=[InputRequired('Must choose your leaving date')])
    origination = StringField('From', validators=[InputRequired('Must select one from the list')])
    destination = StringField('To', validators=[InputRequired('Must select one from the list')])
    flightnumber = StringField('Flight Number')
    requesttext = TextAreaField('Request Content')
    moneyamount = SelectField('Reward($)', choices=[('<i class="em em-beers"></i> I can offer a hug and a beer','Hug and Beer'),('<i class="em em-sushi"></i> Let me grab you some food and have a nice talk', 'Smile and Food'),("<i class='em em-moneybag'></i> $0 - $15", "$0 - $15"),("<i class='em em-moneybag'></i> $16 - $40", "$16 - $40"),("<i class='em em-moneybag'></i> above $40","above $40"),("<i class='em em-love_letter'></i> Contact me for details", "Other")], default = '<i class="em em-beers"></i> I can offer a hug and a beer')
    contact = StringField('Contact Email')
    def validate_contact(self, field):
        if request.form.get('flightnumber') == '':
            contact_info = request.form.get('contact')
            try:
                v = validate_email(contact_info, allow_smtputf8 = False)
                email = v["email"]
            except EmailNotValidError as e:
                #email is not valid, exception message is human readable
                raise ValidationError(str(e))
    def validate_flightnumber(self, filed):
        if request.form.get('flightnumber') != '':
            nospacenumber = "".join(request.form.get('flightnumber').split())
            flightnumberlower = nospacenumber.lower()
            rexobj = re.compile(r"^([a-z][a-z]|[a-z][0-9]|[0-9][a-z])([a-z]?[0-9]{1,4}[a-z]?)$")
            result = rexobj.match(flightnumberlower)
            if not result:
                raise ValidationError('The flight number you entered is not valid.')
    def validate_origination(self, field):
        user_input = request.form.get('origination')
        airport_exist = Airport.query.filter_by(airport_name=user_input).all()
        if not airport_exist:
            raise ValidationError('You have to SELECT one airport from the dropdown list')
    def validate_destination(self, field):
        user_input = request.form.get('destination')
        airport_exist = Airport.query.filter_by(airport_name=user_input).all()
        if not airport_exist:
            raise ValidationError('You have to SELECT one airport from the list')
        if request.form.get('origination') == request.form.get('destination'):
            raise ValidationError('How can you fly within the same city?')
    def validate_startdate(self, field):
        user_date = request.form.get('startdate')
        user_flightnumber = request.form.get('flightnumber').upper()
        exists = Schedule.query.filter_by(username = current_user.username, startdate = user_date, flightnumber = user_flightnumber).first()
        if exists:
            raise ValidationError('You already have this flight on this date saved in your dashboard.')

class Chatform(FlaskForm):
    requesttext = TextAreaField('Request Content', validators=[InputRequired('You have to write something here')]) 
    moneyamount = SelectField('Reward($)', choices=[('<i class="em em-beers"></i> I can offer a hug and a beer','Hug and Beer'),('<i class="em em-sushi"></i> Let me grab you some food and have a nice talk', 'Smile and Food'),('<i class="em em-moneybag"></i> $0 - $15', '$0 - $15'),('<i class="em em-moneybag"></i> $16 - $40', '$16 - $40'),('<i class="em em-moneybag"></i> above $40','above $40'),('<i class="em em-love_letter"></i> Contact me for details', 'Other')], default = '<i class="em em-beers"></i> I can offer a hug and a beer')
    email = StringField('Contact Email', validators = [InputRequired('Email address is required!'), Email("Invalid Email Address")])

class ContactForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired('Please enter your name')])
    email = StringField("Email", validators=[InputRequired('Please enter your email address'), Email("Invalid Email Address")])
    subject = StringField("Subject", validators=[InputRequired('Please enter a subject')])
    message = TextAreaField("Message", validators=[InputRequired('Please enter a message')])
    submit = SubmitField("Send")

class Roomuser(object):
    def __init__(self, userid = "unknown_id", username="unknown_name", in_room="unknown_room", status = "unknown_status", ifunread = 0):
        self.userid = userid
        self.username = username
        self.in_room = in_room
        self.status = status
        self.ifunread = ifunread
    def __repr__(self):
        return '<Roomuser object. Username is {0}, in_room {1}, status {2}, ifunread {3}>'.format(self.username, self.in_room, self.status, self.ifunread)

