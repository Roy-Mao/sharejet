![Imgur](https://i.imgur.com/FABr4FC.png)
# About this project  
Share-Jet is an open source  project that can help you find people on the next flight so that people can help each other such as:  

1. Chatting with people on the same flight before your travel.
    * Rearrange your suitcase by finding people on the same flight.
    * Hitch a ride to and from the airport.
    * Seat Exchange and find your local guidance
    * Make new friends and find your travelling companion.
2. Find people for your overseas purchasing. 
    * If you are taking a flight, help people bring their stuff and get your reward.
    * If you need urgent delivery, find the people on the next flight and tell them your need.

## Language and Environment

* Backend: python(3.6)
* Frontend: Javascript(6.11.0)
* OS: macOS 10.13 (17A365) 64bits
* Database: Postgres(9.6.5)
* FileStorage: AWS S3  
* Deployed on Heroku
* Website: https://sharejet.herokuapp.com



##Directory Structure
```
root
│   .com.apple.timemachine.supported
│   .gitignore
|   Procfile
|   README.md
|   USERGUID.md
|   airports.csv
|   babel.cfg
|   helpers.py
|   postgresv1.db
|   requirements.txt
|   run.py
|
└───myapp
|  |  __init.py__
|  |  configmodule.py
|  |  flaskform.py
|  |  messages.pot
|  |  models.py
|  |  views.py
|
|  └───static
|  │   img
|  │   aboutus.css
|  |   bugcs.css
|  |   contactus.css
|  |   favicon.ico
|  |   ie1--viewport-bug-workaround.js
|  |   ihover.min.css
|  |   info.js
|  |   jquery.emojipicker.a.css
|  |   jquery.emojipicker.css
|  |   jquery.emojipicker.js
|  |   jquery.emojis.js
|  |   jquery.rotate.js
|  |   lanset.js
|  |   mychat.css
|  |   mychat.js
|  |   myprofile.css
|  |   myprofile.js
|  |   officeloc.css
|  |   quote.js
|  |   styles.css
|  |   userguid.js
|  |   welcome.css
|  |
|  └───templates
|  |   _formhelpers.html
|  |   aboutus.html
|  |   apology.html
|  |   contactus.html
|  |   info.html
|  |   layout.html
|  |   login.html
|  |   mychat.html
|  |   myprofile.html
|  |   officeloc.html
|  |   quote.html
|  |   register.html
|  |   resetpw.html
|  |   thehelp.html
|  |   upload.html
|  |   welcome.html
|  |
|  └───translations
|  └───ja/LC_MESSAGES
|  |   |   messages.mo
|  |   |   messages.po
|  |   
|  └───zh_CN/LC_MESSAGES
|  |   |   messages.mo
|  |   |   messages.po
```

## Questions
You can contact me if you have and concerns or questions regarding to  this web application.

* facebook: [@Roymao](https://www.facebook.com/ruoyu.mao)
* email: <ruoyu.mao@icloud.com>
* WeCaht:    
    ![Imgur](https://i.imgur.com/hGWmAef.jpg)
* Line:  
    ![Imgur](https://i.imgur.com/r8KSz5S.jpg)

## To be improved
* Need better Database design and native application support for better user experience.
* More rigerous user input check. eg:space at the end of email should be illegal.
* More languages support(Spanish/German) and theme available in the future.
* I find it difficult to fully understand flask-socketio. Worried that this app won't work smoothly if users amount reach a certain level.
 Heroku seems to be blocked by the great fire wall. Maybe need to use another Pass instead of Heroku to have better access to mainland China.
* Difficult to get the flight number info so that there is no way validating the flight number a user entered is correct or not. The user is responsible to make sure if the flight number they entered is absolutely correct.
* I know my python code is way too dirty. Please help me correct my code after laughing at me.
* [Roy's github](https://github.com/Roy-Mao/sharejet)

## Appreciation
Special thanks to:

* [CS50 Community](https://www.facebook.com/cs50/)
* [David J. Malan ](https://cs.harvard.edu/malan/) 
* [Ryan Brill](https://www.facebook.com/cs50/)
* [Miguel Grinberg Flask Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
* [Pretty Print youtube videos](https://www.youtube.com/channel/UC-QDfvrRIDB6F0bIO4I4HkQ)


