
/*! jquery.cookie v1.4.1 | MIT */
!function(a){"function"==typeof define&&define.amd?define(["jquery"],a):"object"==typeof exports?a(require("jquery")):a(jQuery)}(function(a){function b(a){return h.raw?a:encodeURIComponent(a)}function c(a){return h.raw?a:decodeURIComponent(a)}function d(a){return b(h.json?JSON.stringify(a):String(a))}function e(a){0===a.indexOf('"')&&(a=a.slice(1,-1).replace(/\\"/g,'"').replace(/\\\\/g,"\\"));try{return a=decodeURIComponent(a.replace(g," ")),h.json?JSON.parse(a):a}catch(b){}}function f(b,c){var d=h.raw?b:e(b);return a.isFunction(c)?c(d):d}var g=/\+/g,h=a.cookie=function(e,g,i){if(void 0!==g&&!a.isFunction(g)){if(i=a.extend({},h.defaults,i),"number"==typeof i.expires){var j=i.expires,k=i.expires=new Date;k.setTime(+k+864e5*j)}return document.cookie=[b(e),"=",d(g),i.expires?"; expires="+i.expires.toUTCString():"",i.path?"; path="+i.path:"",i.domain?"; domain="+i.domain:"",i.secure?"; secure":""].join("")}for(var l=e?void 0:{},m=document.cookie?document.cookie.split("; "):[],n=0,o=m.length;o>n;n++){var p=m[n].split("="),q=c(p.shift()),r=p.join("=");if(e&&e===q){l=f(r,g);break}e||void 0===(r=f(r))||(l[q]=r)}return l};h.defaults={},a.removeCookie=function(b,c){return void 0===a.cookie(b)?!1:(a.cookie(b,"",a.extend({},c,{expires:-1})),!a.cookie(b))}});




var tour = new Tour({
  name: "tour",
  steps: [
  {
    title: 'Welcome to PandaJet',
    content: "Let's get started! 🤔",
    backdrop: true,
    orphan: true
  },

  {
    element: "#guide1",
    title: "Step 1: Search the flight",
    content: "Easy! First you need to join a chatting room or send a request to other users by clicking Flight Chat",
    reflex: true,
    //backdrop: true
  },
  {
    path:Flask.url_for('quote'),
    element: "#headingOne",
    title: "Step 2: Join the room.",
    content: "If you are taking a flight, type in your flight number and find who is on the same flight with you and chat with them",
    //backdrop: true,
    onShow: function(){$('#headingOne').find('a').click()},
    onHide: function(){$('#headingTwo').find('a').click()}
  },
  {
    path: Flask.url_for('quote'),
    element:"#headingTwo",
    title: "Step 2: Delivery Request",
    content: "Or if you are not taking any flights, you can click this to initiate a delivery request. Then your request will be broadcast to all people on this specific route and on this particular date",
    onHide: function(){$('#headingTwo').find('a').click()}
  },
  {
    path: Flask.url_for('index'),
    element:"#guide3",
    title: "Step 3: Your Activities",
    content: "You can check all your flight schedules and manipulate all your requests in your dashboard.",
    reflex: true
  },
  {
    element:"#first_table",
    title: "Step 4: All your flight schedules",
    content: "You can either delete your schedule or join your flight chatting room.",
    backdrop: true
  },
  {
    element:"#second_table",
    title: "Step 5: All your requests",
    content: "You can either edit or delete your delivery or other requets here",
    backdrop: true
  },
  {
    path: Flask.url_for('thehelp'),
    element:"#guide6",
    title: "Step 6: How can you help?",
    content: "If you have a flight schedule, you refer to this section to see who need your help",
    reflex: true
  },
  {
    element:"#first_table",
    title: "Step 7: Same Flight Requests",
    content: "These are the requests from the flights that you are gonna take. Click to chat online with them",
    backdrop: true
  },
  {
    element:"#second_table",
    title: "Step 8: Other Requests",
    content: "Or maybe the requests are from other people. Just one click to send them an email if you can help.",
    backdrop: true
  },
  {
    path: Flask.url_for('contactus'),
    element:"#bitcoin_qr",
    title: "Step 9: Contact Donation ",
    content: "Your donation and help are very much appreciated. Contact us and we can post your photo here too."
  },
  {
    path:Flask.url_for('quote'),
    element:"#guide10",
    title: "Step 10: User Guide",
    content: "Finally,You are always welcome to check this user guide by clicking here"
    //backdrop: true
  }
  ],
  container:"body",
  smartPlacement: true
});

tour.init()


starttour = function()
{
  if (tour.ended())
  {
    //alert('it is ended detected')
    tour.restart()
  }
  else
  {
  tour.start(true);
  }
}

/*var options = {expires: 1};
if ($.cookie('visits') == null)
{
  starttour();
  $.cookie('visits', '1', options);
}*/