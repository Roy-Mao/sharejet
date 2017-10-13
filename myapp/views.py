# -*- coding: UTF-8 -*-
from flask import flash, redirect, render_template, request, session, url_for, jsonify, make_response, abort
from flask_mail import Message
from flask_babel import gettext as _
from flask_socketio import emit, send, join_room, leave_room
from flask_login import login_user, login_required, logout_user, current_user
from flask_bootstrap import WebCDN
from passlib.apps import custom_app_context as pwd_context
from datetime import date, timedelta, datetime
from sqlalchemy import desc
from email.mime.text import MIMEText
from itsdangerous import SignatureExpired, BadTimeSignature
from botocore.client import Config
from helpers import *
from .flaskform import *
from .models import *
from . import app, db, babel, mail, jsglue, login_manager, photos, heroku, s, socketio
import re, json, jsonpickle, time, os, base64, shutil, boto3, smtplib, pyimgur, sys, mimetypes

"""
#SOME CONSTANT VALUES
"""
IMGUR_CLIENT_ID="339440773e3adf7"
ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
ACCESS_SECRET_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
BUCKET_NAME = os.environ['S3_BUCKET']
login_manager.login_view = 'login'
app.jinja_env.filters["usd"] = usd
app.extensions['bootstrap']['cdns']['jquery'] = WebCDN('//cdn.bootcss.com/jquery/3.2.1/')


"""
#TO ENSURE RESPONSES ARE NOT CACHED IF APP IS IN DEBUG MODE
#SET THE DEFAULT LANGUAGE FOR FLASK-BABEL
"""
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

@babel.localeselector
def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
        if session['lang'] not in ('ja', 'zh', 'en'):
            return abort(404)
    return session.get('lang', 'en')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def welcome():
    return render_template('welcome.html')

@app.route("/index")
@login_required
def index():
    query = request.args.get('request_id')
    oot = request.args.get('request_oot')
    if oot == 't':
        delete_record = Flyreq.query.filter_by(id = query).first()
        db.session.delete(delete_record)
        db.session.commit()
        response_data = {"message": "This record has been deleted successfully from your dashboard."}
        return jsonify(response_data)
    if oot == 'o':
        delete_record = Schedule.query.filter_by(id = query).first()
        db.session.delete(delete_record)
        db.session.commit()
        response_data = {"message": "This record has been deleted successfully from Schedule"}
        return jsonify(response_data)
    #adding this query is for the userid parameter and based on the userid I can get the user profile picture showni the info page
    user_obj = User.query.filter_by(username = current_user.username).first()
    userid = user_obj.id
    #these two query will be executed no matter what. They query the current user's schedule and request record in the database
    #The query should use user's id instead of user name. why? user delete then same name user register will saw previous record
    user_sche_list = Schedule.query.filter_by(username = current_user.username).all()
    user_reque_list = Flyreq.query.filter_by(username = current_user.username).all()
    #here to initialize broadcast_to to [] is necessary because if yuo do not define this here, the return render_template function may not be functioning
    #the reason is that the user_reque_list might be an empty list and thus evaluated to be false
    broadcast_to = []
    if user_reque_list:
        for each_reque in user_reque_list:
            inner_list = []
            if each_reque.flightnumber == '':
                from_city = each_reque.leaving_city
                to_city = each_reque.arriving_city
                on_date = each_reque.event_date
                flight_list = Schedule.query.filter_by(leaving_city=from_city, arriving_city=to_city, startdate = on_date).all()
                for each_flight in flight_list:
                    each_num = each_flight.flightnumber
                    if not each_num in inner_list:
                        inner_list.append(each_num)
            if each_reque.flightnumber != '':
                inner_list.append(each_reque.flightnumber)
            broadcast_to.append(inner_list)
    return render_template('info.html', user_sche_list = user_sche_list, user_reque_list = user_reque_list, broadcast_to = broadcast_to, userid = userid)



#This is a route used to handle the posted form(from mychat.html) or x-editable ajax request (from info.html)
#the request.method of both should be post, so there is no need for get
@app.route('/flyreq', methods = ['POST'])
@login_required
def flyreq():
    #this is for the use in the formation of mychat.html
    form = Chatform()
    userid = current_user.id
    leaving_city = request.form.get('leaving_city')
    arriving_city = request.form.get('arriving_city')
    flightnumber = request.form.get('flightnumber')
    #the event_date here contains /, not pure number. It comes form the mychat.js my_text constant
    event_date = request.form.get('event_date')
    #It will first check if the method is post and the form is valid, if it is valid it means the post request comes form the info.html join flight button post
    if form.validate_on_submit():
        username = request.form.get('username')
        requesttext = form.requesttext.data
        moneyamount = form.moneyamount.data
        email = form.email.data
        new_flyreq = Flyreq(username = username, leaving_city = leaving_city, arriving_city = arriving_city,
            flightnumber = flightnumber, event_date = event_date, requesttext = requesttext, moneyamount = moneyamount,
            email = email)
        db.session.add(new_flyreq)
        db.session.commit()
        flash("Your request has been added into your dashboard.")
        return render_template('mychat.html', userid = userid, leaving_city=leaving_city, arriving_city=arriving_city, startdate=event_date, flightnumber=flightnumber, form=form)
    # if form.validate_on_submit() evaluates to false, one possibility is that it is an ajax request from the a ajax x-editable plug-in
    # to check if it is an expected ajax request, we add the following conditions
    else:
        if request.form.get('pk'):
            fieldname = request.form.get('name')
            primary_key = int(request.form.get('pk'))
            new_value = request.form.get('value')
            target_record = Flyreq.query.filter_by(id = primary_key).first()
            if fieldname == 'requesttext':
                target_record.requesttext = new_value
            elif fieldname == 'moneyamount':
                target_record.moneyamount = new_value
            else:
                return jsonify(success = "The connection is good but ajax value sent to server is unrecoganizable")
            db.session.commit()
            return jsonify(success = 'Everything is perfect and ajax update the requesttext successfully')
        #if it is not an ajax request, then it must be the form submitted is truely invalide.
        # Therefore we can return an html back to the client indicating the error
        flash("The form you just submitted contain invalid value, check again.")
        return render_template("mychat.html", leaving_city=leaving_city, arriving_city=arriving_city, startdate=event_date, flightnumber=flightnumber, form=form)

    #flash("Something went wrong, please try to resubmit your request again.")
    #return redirect(url_for('index'))


@app.route('/thehelp', methods = ['GET','POST'])
@login_required
def thehelp():
    username = current_user.username
    user_obj = User.query.filter_by(username = username).first()
    userid = user_obj.id
    #the form posted to this route does not contain the helper name and the helper email. These two data is retrieve within this route function
    if request.method == 'POST':
        this_user_obj = User.query.filter_by(username = username).first()
        helpeename = request.form.get('helpeename')
        helpername = username
        helper_email = this_user_obj.email
        helpee_email = request.form.get('helpee_email')
        leaving_city = request.form.get('leaving_city')
        arriving_city = request.form.get('arriving_city')
        event_date = request.form.get('event_date')
        flightnumber = request.form.get('flightnumber')
        requesttext = request.form.get('requesttext')
        moneyamount = request.form.get('moneyamount')
        from_port = request.form.get('from_port')
        to_port = request.form.get('to_port')
        send_html = """
<!DOCTYPE html>
<html>
    <head>
    <meta charset="utf-8" />
        <style>
            #outlook a{padding:0;}
            body{width:100% !important; background-color:#41849a;-webkit-text-size-adjust:none; -ms-text-size-adjust:none;margin:0 !important; padding:0 !important;}  
            .ReadMsgBody{width:100%;} 
            .ExternalClass{width:100%;}
            ol li {margin-bottom:15px;}
            img{height:auto; line-height:100%; outline:none; text-decoration:none;}
            #backgroundTable{height:100% !important; margin:0; padding:0; width:100% !important;}
            p {margin: 1em 0;}
            h1, h2, h3, h4, h5, h6 {color:#222222 !important; font-family:Arial, Helvetica, sans-serif; line-height: 100% !important;}
            table td {border-collapse:collapse; padding: 5px;}
            table th {border-collapse:collapse; padding: 5px;}
            caption {font-size: 20px; font-family: Arial,Helvetica,sans-serif; margin-bottom: 10px; margin-top: 10px;}
            .yshortcuts, .yshortcuts a, .yshortcuts a:link,.yshortcuts a:visited, .yshortcuts a:hover, .yshortcuts a span { color: black; text-decoration: none !important; border-bottom: none !important; background: none !important;}
            .im {color:black;}
            .redi {color: red; text-decoration: underline; font-style: italic;}
            .jhead {color: black; font-size: 40px; font-family: "Arial Black", Gadget, sans-serif; letter-spacing: 5px}
            .shead {color: #5E5E5E; font-size: 40px; letter-spacing: 5px;}
            div[id="tablewrap"] {
                    width:100%; 
                    max-width:600px!important;
                }
            table[class="fulltable"], td[class="fulltd"] {
                    max-width:100% !important;
                    width:100% !important;
                    height:auto !important;
                }       
            @media screen and (max-device-width: 430px), screen and (max-width: 430px) { 
                    td[class=emailcolsplit]{
                        width:100%!important; 
                        float:left!important;
                        padding-left:0!important;
                        max-width:430px !important;
                    }
                td[class=emailcolsplit] img {
                margin-bottom:20px !important;
                }
            }
        </style>
    </head>
    <body style="width:100% !important; margin:0 !important; padding:0 !important; -webkit-text-size-adjust:none; -ms-text-size-adjust:none; background-color:#FFFFFF;">
        <table cellpadding="0" cellspacing="0" border="0" id="backgroundTable" style="height:auto !important; margin:0; padding:0; width:100% !important; background-color:#FFFFFF; color:#222222;">
            <tr>
                <td>
                    <div id="tablewrap" style="width:100% !important; max-width:600px !important; text-align:center !important; margin-top:0 !important; margin-right: auto !important; margin-bottom:0 !important; margin-left: auto !important;">
                        <table id="contenttable" width="600" align="center" cellpadding="0" cellspacing="0" border="0" style="background-color:#FFFFFF; text-align:center !important; margin-top:0 !important; margin-right: auto !important; margin-bottom:0 !important; margin-left: auto !important; border:none; width: 100% !important; max-width:600px !important;">
                            <tr>
                                <td width="100%">
                                    <table bgcolor="#FFFFFF" border="0" cellspacing="0" cellpadding="0" width="100%">
                                        <tr>
                                            <td width="100%" bgcolor="#ffffff" style="text-align:center;"><p><span class= "jhead">SHARE</span><span class= "shead"><b>JET</b></span></p>
                                                <div style = "width:100%; color:#586883; font-family:cursive,Arial,Helvetica,sans-serif"> Build Trust and Connections among world travellers</div>
                                                <hr>
                                            </td>
                                        </tr>
                                   </table>
                                   <table bgcolor="#FFFFFF" border="0" cellspacing="0" cellpadding="25" width="100%">
                                        <tr>
                                            <td width="100%" bgcolor="#ffffff" style="text-align:left;">
                                                <p style="color:#222222; font-family:Arial, Helvetica, sans-serif; font-size:15px; line-height:19px; margin-top:0; margin-bottom:20px; padding:0; font-weight:normal;">
                                                    This email is sent to both <b>""" + helpeename + """</b> and <b>""" + helpername + """</b>:                            
                                                </p>
                                                <p style="color:#222222; font-family:Arial, Helvetica, sans-serif; font-size:15px; line-height:19px; margin-top:0; margin-bottom:0; padding:0; font-weight:normal;">
                                                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Hey <b>""" + helpeename + """</b>, one of your request post on ShareJet got a response from user: <b>""" + helpername + """</b>. The user saw your post and confirmed that """ + helpername + """ might be able to help. Please <span class = "redi">contact """ +  helpername + """ directly via """ + helpername + """&#39;s email</span> if you still need help (do not reply to this email). """ + helpername + """&#39;s contact information is displayed in the table below. If you already solved your problem, you can always delete your request in your ShareJet account dashboard, so that no one would see your request (^_^): 
                                                </p>
                                            </td>
                                        </tr>
                                   </table>
                                    <table border="1" cellspacing="0" cellpadding="0" width="100%">
                                        <caption><b>User Request</b></caption>
                                          <tr>
                                            <th>Username</th>
                                            <th>Contact(email)</th>
                                            <th>Pay(dollar)</th>
                                          </tr>
                                          <tr>
                                            <td>""" + helpeename + """</td>
                                            <td>""" + helpee_email + """</td>
                                            <td>""" + moneyamount + """</td>
                                          </tr>
                                          <tr><td colspan = "3">""" + requesttext + """</td></tr>
                                    </table>
                                    <table border="1" cellspacing="0" cellpadding="0" width="100%">
                                        <caption><b>Helper Information</b></caption>
                                          <tr>
                                            <th>Helper name</th><td>""" + helpername + """</td>
                                          </tr>
                                          <tr>
                                            <th>Flightnumber</th><td>""" + flightnumber + """</td>
                                          </tr>
                                          <tr>
                                            <th>From airport</th><td>""" + from_port + """</td>
                                          </tr>
                                          <tr>
                                            <th>To airport</th><td>""" + to_port + """</td>
                                          </tr>
                                          <tr>
                                            <th>Date</th><td>""" + event_date + """</td>
                                          </tr>
                                          <tr>
                                            <th>Contact(email)</th><td>""" + helper_email + """</td>
                                          </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>
                        <table bgcolor="#FFFFFF" border="0" cellspacing="0" cellpadding="0" width="100%">
                            <tr>
                                <td width="100%" bgcolor="#ffffff" style="text-align:center;"><a style="font-weight:bold; text-decoration:none;" href="#"><div style="display:block; max-width:100% !important; width:93% !important; height:auto !important;background-color:#2489B3;padding-top:15px;padding-right:15px;padding-bottom:15px;padding-left:15px;border-radius:8px;color:#ffffff;font-size:24px;font-family:Arial, Helvetica, sans-serif;">Your ShareJet Account</div></a></td>
                            </tr>
                        </table>
                        <table bgcolor="#FFFFFF" border="0" cellspacing="0" cellpadding="25" width="100%">
                            <tr>
                                <td width="100%" bgcolor="#ffffff" style="text-align:center;">
                                    <p style="color:#222222; font-family:Arial, Helvetica, sans-serif; font-size:11px; line-height:14px; margin-top:0; margin-bottom:15px; padding:0; font-weight:normal;">
                                                    Email not displaying correctly? <a style="color:#2489B3; font-weight:bold; text-decoration:underline;" href="#">View it in your browser.</a>
                                    </p>
                                    <p style="color:#222222; font-family:Arial, Helvetica, sans-serif; font-size:11px; line-height:14px; margin-top:0; margin-bottom:15px; padding:0; font-weight:normal;">
                                                    2013-2017 &#169;ShareJet. All Rights Reserved.
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </div>
                </td>
            </tr>
        </table>
    </body>
</html>
"""
        smtp_server = 'smtp.mail.yahoo.com'
        server = smtplib.SMTP(smtp_server)
        server.set_debuglevel(1)
        send_msg = MIMEText(send_html, 'html', _charset='utf-8')
        sender = 'lee.rio@yahoo.com'
        recipients = [helper_email, helpee_email]
        password = 'mr930313y'
        send_msg['Subject'] = "Response from ShareJet user: " + helpername
        send_msg['From'] = sender
        send_msg['To'] = ", ".join(recipients)
        server.ehlo()
        server.starttls()
        server.login(sender,password)
        #Please mind the difference between python2 and python3
        #server.sendmail(sender, recipients, send_msg.as_string())
        server.sendmail(sender, recipients, send_msg.as_bytes())
        server.quit()
        flash_msg = 'A contact email has been sent to ' + helpeename + '. Please be pacient and wait for the response.' 
        flash(flash_msg)
        #time.sleep(3)
    schedule_list = Schedule.query.filter_by(username = username).all()
    mreq_list = []
    oreq_list = []
    each_schedule_fn = ''
    each_schedule_la = ''
    each_schedule_aa = ''
    for each_schedule in schedule_list:
        each_schedule_lc = each_schedule.leaving_city
        each_schedule_ac = each_schedule.arriving_city
        each_schedule_la = each_schedule.origination
        each_schedule_aa = each_schedule.destination
        each_schedule_tm = each_schedule.startdate
        each_schedule_fn = each_schedule.flightnumber
        match_mreq = Flyreq.query.filter_by(leaving_city = each_schedule_lc, arriving_city = each_schedule_ac, event_date = each_schedule_tm, flightnumber = '').all()
        match_oreq = Flyreq.query.filter_by(event_date = each_schedule_tm, flightnumber = each_schedule_fn).all()
        mreq_list.extend(match_mreq)
        oreq_list.extend(match_oreq)
    return render_template('thehelp.html', match_mreq = mreq_list, match_oreq = oreq_list, fn = each_schedule_fn, from_port = each_schedule_la, to_port = each_schedule_aa, userid = userid)


@app.route('/upload', methods=['POST','GET'])
@login_required
def upload():
    if request.method == 'POST':
        filename = photos.save(request.files['image'])
        filepath = photos.path(filename)
        im = pyimgur.Imgur(IMGUR_CLIENT_ID)
        uploaded_image = im.upload_image(filepath, title=filename)
        os.remove(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename))
        uppic_url =  uploaded_image.link
        return jsonify(
            fromuser = request.form['fromuser'],
            touser = request.form['touser'],
            img_url = uppic_url
            )
    else:
        return redirect(url_for('index'))

@app.route('/propic', methods=['POST','GET'])
@login_required
def propic():
    if request.method == "POST" and request.mimetype == "application/json":
        pic_data = json.loads(request.data)['picstring']
        name_data =json.loads(request.data)['this_user']
        query_obj = User.query.filter_by(username = name_data).first()
        file_name = str(query_obj.id) + '_pf.png'
        image_data = re.sub('^data:image/.+;base64,', '', pic_data)
        de_data = bytes(image_data, encoding="ascii")
        script_dir = os.path.dirname(os.path.dirname(__file__)) #absolute dir the script is in
        abs_file_path = '/tmp/' + file_name
        #abs_file_path = os.path.join(script_dir, rel_path)
        #print ('llllllllllllllll-------------kankanjuedui')
        #print (abs_file_path)
        try:
            with open(abs_file_path, "wb") as fh:
                fh.write(base64.decodebytes(de_data))
                data = open(abs_file_path,'rb')
                s3 = boto3.resource('s3', aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=ACCESS_SECRET_KEY, config=Config(signature_version='s3v4'))
                s3.Bucket(BUCKET_NAME).put_object(Key=file_name, Body=data, ACL='public-read')
                os.remove(abs_file_path)
                return jsonify({"message":"Server received client message succesfully updated."})
        except:
            flash ("Couldn't open or write to file. Please try again.") 
            return render_template('myprofile.html')
    else:
        #flash('upload picture failed, maybe try it again?')
        return redirect(url_for('myprofile'))




@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        this_user = User.query.filter_by(email = form.email.data).first()
        login_user(this_user, remember = form.remember.data)
        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.
        if 'next' in session:
            next = session['next']
            if not is_safe_url(next):
                return abort(400)
            return redirect(next)
        return redirect(url_for('index'))
    if request.args.get('next') is not None:
        session['next'] = request.args.get('next')
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    else:
        return render_template('login.html', form=form)
    #return redirect(url_for('index'))



@app.route("/logout")
def logout():
    logout_user()
    # redirect user to login form
    flash("You are now logged out.")
    return redirect(url_for("login"))


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    form = SearchForm()
    #the validate_on_submit method actually checks for the post already
    if form.validate_on_submit():
        username = current_user.username
        startdate = form.startdate.data
        origination = form.origination.data
        destination = form.destination.data
        flightnumber = (form.flightnumber.data).upper()
        moneyamount = form.moneyamount.data
        requesttext = form.requesttext.data
        contact = form.contact.data
        leaving_obj = Airport.query.filter_by(airport_name = origination).first()
        leaving_city = leaving_obj.city
        arriving_obj = Airport.query.filter_by(airport_name = destination).first()
        arriving_city = arriving_obj.city
        if requesttext == '':
            new_schedule = Schedule(username = username, startdate = startdate, origination = origination, destination = destination,
                                flightnumber = flightnumber, leaving_city = leaving_city, arriving_city = arriving_city)
            db.session.add(new_schedule)
            db.session.commit()
            flash("Your flight schedule has been added into your dashboard.")
        else:
            new_flyreq = Flyreq(username = username, event_date = startdate,
                                flightnumber = flightnumber, leaving_city = leaving_city, arriving_city = arriving_city,
                                moneyamount = moneyamount, requesttext = requesttext, email = contact)
            db.session.add(new_flyreq)
            db.session.commit()
            flash("Your request has been added into your dashboard")
        return redirect(url_for('index'))
    return render_template("quote.html", form = form)


@app.route("/mychat",  methods=["GET", "POST"])
@login_required
def mychat():
    username = current_user.username
    user_obj = User.query.filter_by(username = username).first()
    userid = user_obj.id
    form = Chatform()
    if request.method == 'POST':
        leaving_city = request.form.get('leaving_city')
        arriving_city = request.form.get('arriving_city')
        startdate = request.form.get('startdate')
        flightnumber = request.form.get('flightnumber')
        if (leaving_city and arriving_city and startdate and flightnumber):
            return render_template("mychat.html", userid = userid, leaving_city=leaving_city, arriving_city=arriving_city, startdate=startdate, flightnumber=flightnumber, form=form)
    return redirect(url_for('index'))



@app.route("/search")
@login_required
def search():
    #"""Search for places that match query."""
    query = request.args.get('q')
    if query:
        results = []
        search_this = '%' + query + '%'
        airport_list = Airport.query.filter((Airport.city.ilike(search_this)) | Airport.airport_name.ilike(search_this)).limit(10).all()
        for airport in airport_list:
            serialized = jsonpickle.encode(airport)
            stod = json.loads(serialized)
            results.append(stod)
        return jsonify(results)
    return redirect(url_for('quote'))


@app.route("/history")
@login_required
def history():
    receiver = request.args.get('receiver')
    sender = request.args.get('sender')
    ifunread = request.args.get('ifunread')
    which_room = request.args.get('which_room')
    #check where the request comes from. If they are receiver and sender, then it comes from the check_history method in mychat.js
    #then update the read_status of this message from unread to read. 0 to 1.
    if receiver and sender:
        latest_msg = History.query.filter_by(receiver = receiver, sender = sender).order_by(desc(History.id)).first()
        #no need to check if it exits because it must exist
        latest_msg.read_status = True
        db.session.commit()
        return jsonify(message = "update read_status successfully")
    #if received request contains ifunread and which_room, then it must comes from the pchat_react method in mychat.js
    #then update the objectin room_users (each object in room_users is actually a Roomuser obj,not saved in database but contains the attribute of ifunread)
    if ifunread and which_room:
        for each_str in socketio.room_users[which_room]:
            each_obj = jsonpickle.decode(each_str)
            if each_obj.username == ifunread:
                old_str = each_str
                each_obj.ifunread = 0
                new_str = jsonpickle.encode(each_obj)
                socketio.room_users[which_room].remove(old_str)
                socketio.room_users[which_room].append(new_str)
                return jsonify(message = "update ifunread successfully")
    return redirect(url_for('index'))



@app.route("/register", methods=["GET", "POST"])
def register():
    #-------------Better way using Flask-WTForms---------------
    form = RegistrationForm()
    if form.validate_on_submit():
        user_email = form.email.data
        user_name = form.username.data
        user_psw = form.password.data
        encrypt_psw = pwd_context.encrypt(user_psw)
        new_user = User(username = user_name, email = user_email, hashed = encrypt_psw, confirm_email = False)
        db.session.add(new_user)
        db.session.commit()
        token = s.dumps(user_email, salt='email-confirm')
        msg = Message('Confirm Email', sender='lee.rio@yahoo.com', recipients=[user_email])
        link = url_for('confirm_email', token=token, _external=True)
        #msg.body = 'Your confirmation link is {}'.format(link)
        msg.body = 'This is ShareJet, your confirmation link is: {} Click the link (or paste it into your browser) to activate your account in ShareJet.'.format(link)
        mail.send(msg)
        flash('We sent a validation letter to your email at {}.(It might cost some time) Please verify it within 30 minutes and be sure to check your junk mail'.format(user_email))
        return redirect(url_for('login'))
    return render_template('register.html', form = form)


@app.route("/confirm_email/<token>")
def confirm_email(token):
    try:
        user_email = s.loads(token, salt='email-confirm', max_age = 1800)
    except SignatureExpired:
        flash('30 minutes time has expired. The link is no longer valid.')
        return redirect(url_for('login'))
    except BadTimeSignature:
        flash('The URL seems incorrect.Did you change it?')
        return redirect(url_for('login'))
    cur_user = User.query.filter_by(email = user_email).first()
    login_user(cur_user)
    # once the user confirm the email. Give a user a default profile picutre
    file_name = str(cur_user.id) + '_pf.png'
    script_dir = os.path.dirname(__file__) #absolute dir the script is in
    #rel_path_new = "static/img/proimg/" + file_name
    #abs_file_path_new = os.path.join(script_dir, rel_path_new)
    rel_path_old = "static/img/default_dpf.png"
    abs_file_path_old = os.path.join(script_dir, rel_path_old)
    data = open(abs_file_path_old, 'rb')
    s3 = boto3.resource('s3', aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=ACCESS_SECRET_KEY, config=Config(signature_version='s3v4'))
    s3.Bucket(BUCKET_NAME).put_object(Key=file_name, Body=data, ACL='public-read')
    #shutil.copyfile(abs_file_path_old, abs_file_path_new)
    current_user.confirm_email = True
    db.session.commit()
    data.close()
    flash('Email validation succeed! Thanks for registering.')
    return redirect(url_for('login'))


@app.route("/officeloc")
def officeloc():
    return render_template('officeloc.html')

@app.route("/aboutus")
def aboutus():
    return render_template('aboutus.html')

@app.route("/contactus", methods = ['GET', 'POST'])
def contactus():
    form = ContactForm()
    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('contactus.html', form = form)
        else:
            msg = Message(form.subject.data, sender='lee.rio@yahoo.com', recipients=['ruoyu.mao@icloud.com'])
            msg.body = """
            From: %s <%s>
            %s
            """ % (form.name.data, form.email.data, form.message.data)
            mail.send(msg)
            return render_template('contactus.html', success = True)
    elif request.method == 'GET':
        return render_template('contactus.html', form = form)

@app.route("/myprofile", methods = ['GET','POST'])
@login_required
def myprofile():
    username = current_user.username
    user_info = User.query.filter_by(username = username).first()
    sameperson = True
    if request.method == 'POST':
        fieldname = request.form.get('name')
        primary_key = int(request.form.get('pk'))
        new_value = request.form.get('value')
        target_record = User.query.filter_by(id = primary_key).first()
        if fieldname == 'username':
            target_record.username = new_value
        else:
            return jsonify(success = "The connection is good but ajax value (name fieldname) sent to server is unrecoganizable")
        db.session.commit()
        return jsonify(success = 'Everything is perfect and ajax update the requesttext successfully')
    if request.method == 'GET':
        browseuser = request.args.get('browsename')
        if browseuser and browseuser != username:
            sameperson = False
            username = browseuser
            user_info = User.query.filter_by(username = username).first()
            if not user_info:
                flash('The user you are searching for does not exist')
                return redirect(url_for('index'))
    return render_template('myprofile.html', username=username, user_email = user_info.email, userid = user_info.id, sameperson = sameperson)




@app.route("/valiedit", methods = ["GET","POST"])
@login_required
def valiedit():
    query = request.args.get('this_value')
    typeidf = request.args.get('this_type')
    if typeidf == 'na':
        query_record = User.query.filter_by(username = query).first()
        if query_record:
            response_data = {"exist": "Exist username, try another one."}
        else:
            response_data = {"normal": "username updated successfully."}

    #elif typeidf == 'em':
    #    query_record = User.query.filter_by(email = query).first()
    #    if query_record:
    #        response_data = {"exist": "Exist email, try another one."}
    #    else:
    #        response_data = {"normal": "email updated successfully"}
    else:
        response_data = {"redirect":"you are updating neither username nor email?"}
    return jsonify(response_data)



        
@app.route("/resetpw", methods = ["GET", "POST"])
@login_required
def resetpw():
    form = ResetpasswordForm()
    if form.validate_on_submit():
        user_id = session['user_id']
        this_user = User.query.filter_by(id=user_id).first()
        user_hash = this_user.hashed
        new_pw = request.form.get('newpassword')
        new_hash = pwd_context.encrypt(new_pw)
        this_user.hashed = new_hash
        db.session.commit()
        flash('You have reset your password successfully.')
        return redirect(url_for('index'))
    return render_template('resetpw.html', form = form)


socketio.room_users = {} #a dictionary, key is the roomidentifier and value is the user(should be the encoded json string) in this room. Actually each is a stringified Roomuser obj
socketio.reqid_info = {} #a dictionary, key is the user request session id and value is the username, roomidentifier related to this 


@socketio.on('connect')
def connect_handler():
    if current_user.is_authenticated:
        emit("handshake_response", {"message": "{0} has been connected".format(current_user.username), "this_user_name":current_user.username}, broadcast=True)
    else:
        return False

@socketio.on('join')
def join_handler(data):
    username = current_user.username #receive join from client and get the client username
    userid = current_user.id
    #user_obj = User.query.filter_by(username = username).first()
    #userid = user_obj.id
    room_public = data['room_id'] #get which room is the user currently in
    user_status = data['status'] #get the current state of this user,(should be online always)
    returned_list = socketio.room_users.setdefault(room_public, []) #give the roomidentifer and return a list of users (each is encoded json)
    returned_name_list =[] #used to store username, becuase each object in returned_list is an encoded json string (jsonpickle)
    returned_name_list.clear() #maybe this is unnecessary
    # CHECK IF THIS ROOM EXIST
    #if this room does not exist, create the room and append this user in this room list
    if not returned_list:
        new_join_user = Roomuser(userid = userid, username = username, in_room = room_public, status = user_status, ifunread = 0) #ifunread means if this user has unread public message, here is set to false
        new_join_user = jsonpickle.encode(new_join_user)
        socketio.room_users[room_public].append(new_join_user)
    #if this room exists, append all the usernames in this room to returned_name_list
    else:
        for each_returned in returned_list:
            old_obj = each_returned
            each_returned = jsonpickle.decode(each_returned)
            returned_name_list.append(each_returned.username)
            # check if this(each) joiner once joined this room or it is his first time in this room. If this joiner is found in the returned list(he joined in the past), update its status to online
            # then encode this joiner, delete the old and append the new (basically update him), new_join_user set to this new_obj
            # IF ROOM EXIST AND THIS USER ONCE IN THE ROOM (REMEMBER IT IS ACTUALLY A ROOMUSER OBJ), NO NEED TO CHANGE ITS IFUNREAD VALUE BUT ONLY TO CHANGE ITS ONLINE STATUS
            if each_returned.username == username:
                each_returned.status = user_status
                new_obj = jsonpickle.encode(each_returned)
                socketio.room_users[room_public].append(new_obj)
                socketio.room_users[room_public].remove(old_obj)
                new_join_user = new_obj
        #THE ROOM EXIST FOR SURE, BUT HERE TO CHECK IF USER ONCE JOINED THIS ROOM
        #if it is the first time for the user to join this already existed room, create a new joiner and append it to the room
        if username not in returned_name_list:
            new_join_user = Roomuser(userid = userid, username = username, in_room = room_public, status = user_status, ifunread = 0)
            new_join_user = jsonpickle.encode(new_join_user)
            socketio.room_users[room_public].append(new_join_user)

    #The above if else condition ensured that there is a new_join_user (encoded json string)
    #because its joining function, every request.sid here should be a new sid. This is used to store the new request.sid and the room/username/status associated with this sid
    socketio.reqid_info.setdefault(request.sid, {}).update({
        'room': room_public,
        'user': username,
        'status': user_status
        })


    #search chatting history in the database
    encode_chat_list = [] #used to store all the encoded private message object
    encode_pchat_list = []
    unread_users = []
    # these three clear method might not be necessary
    encode_chat_list.clear()
    unread_users.clear()
    encode_pchat_list.clear()
    history_list_obj = History.query.filter((History.sender == username) | (History.receiver == username), History.receiver != room_public).order_by(History.ctime).all() #check all the private chatting history related to this user and ordered by latest time
    public_list_obj = History.query.filter_by(receiver = room_public).order_by(History.ctime).all() #check all public chatting history in this specific room and ordered by latest time
    # check if there is any private message related to this user. If it does, encode each message object and append it(astring) to the encode_chat_list
    if history_list_obj:
        for each_obj in history_list_obj:
            encoded_msg_obj = jsonpickle.encode(each_obj)
            encode_chat_list.append(encoded_msg_obj)

    #check if there is any pubic message history given the specific roomidentifier. If it does, encode each public message object and append it(atring) to the encode_pchat_list
    if public_list_obj:
        for each_obj in public_list_obj:
            encoded_pmsg_obj = jsonpickle.encode(each_obj)
            encode_pchat_list.append(encoded_pmsg_obj)

    #if there were some people in this room, then check the database to see if any of them sent messages to this joiner
    # if there existing the searching result then check if the latest message's read_status. If it is 0 (unread message), then append the name to the unread_users list of this user
    if returned_name_list:
        for each_name in returned_name_list:
            sender_latest_msg = History.query.filter_by(receiver = username, sender = each_name).order_by(desc(History.ctime)).first()
            if sender_latest_msg:
                if sender_latest_msg.read_status == False:
                    unread_users.append(each_name)

    join_room(room_public)
    emit("join_response", 
        {
        "joiner_obj": new_join_user, #encode jsonpickle string
        "room_users": socketio.room_users[room_public], #room_public sure to be exist and it is a list containing all the user json pickled object string in this room
        "chat_history": encode_chat_list, #all the private chatting history of this joiner. It is a list, each is the pickled json object string from the database
        "pchat_history": encode_pchat_list,  #all the public chatting histroy in this specific room. It is a list, each is the pickled json object string for the database
        "unread_users": unread_users #a list of this joiner, containing all the usernames of those people this joiner has unread messages from
        }, 
        room=room_public)

#This method is not received from the client but trigerred automatically when the client disconnected
@socketio.on('disconnect')
def disconnect_handler():
    username = socketio.reqid_info[request.sid]['user']  #the key is user while the value should be a username string
    room_public = socketio.reqid_info[request.sid]['room']
    users_list = socketio.room_users[room_public]
    leaving_user_obj = {}
    #loop through every each_person_obj, there must be one's username is the same as the username above
    #find that leaving user in the users_list, which should be a Roomuser obj and then change its status to offline
    #there should be only one object whose username is equal to the username above. Therefore, once found we can break the for loop
    for each_person_obj in users_list:
        old_person_obj = each_person_obj
        each_person_obj = jsonpickle.decode(each_person_obj)
        if each_person_obj.username == username:
            each_person_obj.status = 'offline'
            leaving_user_obj = each_person_obj
            new_person_obj = jsonpickle.encode(each_person_obj)
            socketio.room_users[room_public].append(new_person_obj)
            socketio.room_users[room_public].remove(old_person_obj)
            break
    #encode pickle the leaving_user_obj for emitting purpose.
    serialize_leave_obj = jsonpickle.encode(leaving_user_obj)
    emit("disconnect_response", {"username": username, "leaving_user_obj": serialize_leave_obj}, room = room_public)
    leave_room(room_public)
    #the leaving sid is forever gone from this point, the next time the same user entering this room, he will be assigned a new sid.
    socketio.reqid_info.pop(request.sid)

@socketio.on('my_event')
def handle_my_event(json):
    msg = json["msg"]
    receiver_user = json["receiver_user"]
    sender_user = json["sender_user"]
    room_name = json["room_name"]
    target_user = 2
    #If this message is sent to all passengers
    if receiver_user == room_name:
        target_user = room_name
        for encode_user_obj in socketio.room_users[room_name]:
            decode_user_obj = jsonpickle.decode(encode_user_obj)
            if decode_user_obj.username != sender_user:
                decode_user_obj.ifunread = 1
                old_user_obj = encode_user_obj
                new_user_obj = jsonpickle.encode(decode_user_obj)
                socketio.room_users[room_name].remove(old_user_obj)
                socketio.room_users[room_name].append(new_user_obj)
    #If this message is not sent to all passengers and thus should be a private message
    else:
        #Here k is the session id of each user, the session id can be used as the room id target if for the private chat
        for k, v in socketio.reqid_info.items():
            if v["user"] == receiver_user:
                target_user = k
                break
    # the target_user should not be offline, therefore theritically it should always enter this clause
    if target_user != 2:
        emit("normal_response", {"msg": msg, "sender_user": sender_user, "receiver_user": receiver_user, "room_name": room_name}, room=target_user)
    else:
        print('This user is currently offline, and thus the target_user in handle_my_event is not changed and remains as 2')
        #return False
    millis = int(round(time.time()*1000))
    msg_history = History(message = msg, sender = sender_user, receiver = receiver_user, ctime = millis)
    db.session.add(msg_history)
    db.session.commit()