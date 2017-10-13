
var my_text = $("#set_time").text().trim()
var time_number = my_text.replace(/\D/g,'')
var flight_number = $("#set_number").text().trim()
var this_user = $("#from_user").text().trim()
var room_identifier = time_number + flight_number
var userid = $('#userid').text().trim()

var d = new Date()
//document.getElementsByClassName("img_right_heading").src = "/static/img/proimg/" + userid + "_pf.png?" + d.getTime();
$(".img_right_heading").attr("src","https://s3-ap-northeast-1.amazonaws.com/pandajet/" + userid + "_pf.png?" + d.getTime());

$(function () 
{
	$('[data-toggle="tooltip"]').tooltip()
}
);


$(document).on('keypress', '.pickupaemoji', function(){
	var key = event.which;
	if(key == 13){
		$(event.target).closest('.each_conversation').find('.reply-send').click();
	return false
}})


$(document).on('click', '.fa-question', function(){
	$('.conversation').hide()
	$('#conversation_title').toggle('slide', 800)
})


//this method does not query the database, but check the room_users dictionary and then update the ifunread attribute of each user to tell if there is unread public message.
//but this method has some security concerns along with the check_history() method.(url parameter injection hack.)
pchat_react = function()
{
	var parameters = {
	ifunread : this_user,
	which_room: room_identifier
	}
	$.getJSON(Flask.url_for("history"), parameters)
		.done(function(data){
			console.log(data.message)
	})
		.fail(function(){
			console.log(errorThrown.toString());
		})
}

//this is related the status css in the left users panel.Give the username and find it in the left panel. Change the css according to the small text
user_state_change = function(username)
{
	var user_state_text = $('#sdid_' + username).find('.time-meta').text().trim()
	var save_div = $('#sdid_' + username).get(0)
	// the first part starts from here, it only changes the css style of the user status on the left panel according to the time-meta text value
	if ((user_state_text !== 'message') && (user_state_text !== 'messages'))
	{
		$('#sdid_' + username).find('.time-meta').removeClass('blink_me')
	}
	else 
	{
		$('#sdid_' + username).find('.time-meta').removeClass('offcss')
		$('#sdid_' + username).find('.time-meta').addClass('blink_me')
	}
	if (user_state_text === 'offline')
	{
		$('#sdid_' + username).find('.time-meta').addClass('offcss')
	}
	else
	{
		$('#sdid_' + username).find('.time-meta').removeClass('offcss')
	}
	if (user_state_text === 'online')
	{
		$('#sdid_' + username).find('.time-meta').removeClass('blink_me')
		$('#sdid_' + username).find('.time-meta').removeClass('offcss')
	}
	// the first part ends here, finishing the change of css style
	// the second part starts from here, it will change the position of the user according to each user's time-meta text on the left panel
	// the users' time-meta status should only have these following text value: message/messages/online/offline
	// if the time-meta of that user on the left panel is online or message or messages but that user div is shown in the offline_section, then remove that div -> prepend that user to the online_section
	if (((user_state_text === 'online') || (user_state_text === 'message') || (user_state_text === 'messages')) && ($('#offline_section').find('#sdid_' + username).length == 1))
	{
		$('#sdid' + username).remove()
		$('#online_section').prepend(save_div)
	}
	// if the time-meta of that user on the left panel is offline but that user div is shown in the online_section, then remove that div -> append that userto the offline_section
	if ((user_state_text === 'offline') && ($('#online_section').find('#sdid_' + username).length == 1))
	{
		$('#sdid' + username).remove()
		$('#offline_section').append(save_div)
	}
	// for other cases, there is no need to change the location of that user, just need to change the css style should be sufficient.
	// special case for the user_state_text = '' in the all passenger section. We can leave it there and do not requre any change.
}


get_current_time = function(miliseconds){
	var now
	if (typeof miliseconds === 'undefined')
	{
		now = new Date(Date.now())
	}
	else
	{
		now = new Date(miliseconds)
	}
	var format_hour = (now.getHours()<10?'0':'') + now.getHours()
	var format_minute = (now.getMinutes()<10?'0':'') + now.getMinutes()
	var format_second = (now.getSeconds()<10?'0':'') + now.getSeconds()
	var formatted_time = format_hour + ':' + format_minute + ':' + format_second;
	return formatted_time
}

add_right_page = function(each_obj)
{
	//$('.dynamichtml').empty()
	//joiner_obj = msg.joiner_obj
	var third_d = new Date()
	var create_panel = '\
	<div class="col-sm-8 conversation each_conversation" id = "page_' + each_obj.username + '">\
      <div class="row heading">\
        <div class="col-sm-2 col-md-1 col-xs-3 heading-avatar">\
          <div class="heading-avatar-icon" onclick = "gotopro(browsename=' + '\'' + each_obj.username + '\'' + ')">\
            <img src="https://s3-ap-northeast-1.amazonaws.com/pandajet/' + each_obj.userid + '_pf.png?' + third_d.getTime() + '">\
          </div>\
        </div>\
        <div class="col-sm-8 col-xs-7 heading-name">\
          <a class="heading-name-meta" onclick = "gotopro(browsename=' + '\'' + each_obj.username + '\'' + ')">' + each_obj.username +'</a>' +
	    '</div>\
	    <div class="col-sm-1 col-xs-1  heading-dot pull-right">\
	        <i class="fa fa-question fa-2x  pull-right" aria-hidden="true"></i>\
	    </div>\
	  </div>' +
	  '<div class="row message" id="conversation_' + each_obj.username +'"><p class="no_message">No message yet!</p></div>'+
        '<div class="row reply">\
          <div class="col-sm-1 col-xs-1 reply-emojis" onclick = "chooseEmoji(username=' + '\'' + each_obj.username + '\'' + ')" id = "emoji_trigger_'+ each_obj.username +'">\
            <i class="fa fa-smile-o fa-2x"></i>\
          </div>\
          <div class="col-sm-9 col-xs-9 reply-main">\
            <textarea class="form-control pickupaemoji" rows="1" id="comment_' + each_obj.username + '"></textarea>\
          </div>\
          <div class="col-sm-1 col-xs-1 reply-images">\
          	<form method=POST enctype=multipart/form-data>\
          		<label for="upload_' + each_obj.username + '">\
            		<i class="fa fa-file-image-o fa-2x" aria-hidden="true"></i>\
            	</label>\
            	<input type="file" id = "upload_' + each_obj.username + '" name = "chat_photo" accept="image/*" onchange="chooseUpload(this, username =' + '\'' + each_obj.username + '\'' + ')" capture/>\
            </form>\
          </div>\
          <div class="col-sm-1 col-xs-1 reply-send" onclick = "readytoSend(this, username=' + '\'' + each_obj.username + '\'' + ')">\
            <i class="fa fa-send fa-2x" aria-hidden="true"></i>\
          </div>\
        </div>\
		</div>'
    $('#right_dynamic').append(create_panel)

    $('#comment_' + each_obj.username).emojiPicker({
	width: '200px',
	height: '180px',
	button: false
	});
}




add_chat_history = function(chat_history_str)
{
	if (typeof chat_history_str != "undefined" && chat_history_str != null && chat_history_str.length > 0)
	{
		var each_record_obj;
		var create_message;
		var milliseconds;
		var formatted_time;
		var each_msg;
		var sender_message;
		var receiver_message;
		for (i=0; i<chat_history_str.length; i++ )
		{
			each_record_obj = JSON.parse(chat_history_str[i])
			if (each_record_obj.sender === this_user)
			{
				milliseconds = each_record_obj.ctime
				formatted_time = get_current_time(milliseconds)
				each_msg = each_record_obj.message
				sender_message = '<div class="row message-body">\
	      							<div class="col-sm-12 message-main-sender">\
	        							<div class="sender">\
								        	<div class="message-text">' +
								            	each_msg +
								        	'</div>\
								        	<span class="message-time pull-right">' +
								            	formatted_time +
								        	'</span>'+
								       	'</div>\
								    </div>\
								</div>'		
				$('#conversation_' + each_record_obj.receiver).find('.no_message').remove()
				$('#conversation_' + each_record_obj.receiver).append(sender_message)
			}
			else if (each_record_obj.receiver === this_user)
			{
				milliseconds = each_record_obj.ctime
				formatted_time = get_current_time(milliseconds)
				each_msg = each_record_obj.message
				receiver_message = 	'<div class="row message-body">\
	        							<div class="col-sm-12 message-main-receiver">\
	            							<div class="receiver">\
	            								<div class="message-text">' +
	            									each_msg +
	            								'</div>\
	            								<span class="message-time pull-right">' +
	                								formatted_time +
	            								'</span>\
	            							</div>\
	          							</div>\
	        						</div>'
				$('#conversation_' + each_record_obj.sender).find('.no_message').remove()
				$('#conversation_' + each_record_obj.sender).append(receiver_message)
			}
			else
			{
				alert('Adding private history error, this user is neigher receiver or sender of msg record object<function:add_chat_history>')
			}
		}
	}
	else
	{
		console.log('This user\'s private chat history seems to be zero.(have not received or talk to anyone) <function:add_chat_history>')
	}
}


//only functioning if the pchat_history_str has at least one record (it is actually a list not string)
add_pchat_history = function(pchat_history_str)
{
	//better way to ensure that there is at least one record in the pchat_history_str
	if (typeof pchat_history_str != "undefined" && pchat_history_str != null && pchat_history_str.length > 0)
	{
		var each_record_obj;
		var create_message;
		var milliseconds;
		var formatted_time;
		var each_msg;
		var public_msg;
		for (i=0; i<pchat_history_str.length; i++ )
		{
			each_record_obj = JSON.parse(pchat_history_str[i])
			milliseconds = each_record_obj.ctime
			formatted_time = get_current_time(milliseconds)
			each_msg = each_record_obj.message
			public_msg = '<div class="public_talk"><div class="public_sender">' + each_record_obj.sender + '</div><div class="public_msg">' + each_msg + '</div><span class="message-time pull-right">' + formatted_time + '</span><div class="clear_div"></div></div>'
			$('#conversation_all').find('.no_message').remove()
			$('#conversation_all').append(public_msg)
		}
	}
}


check_history = function(that_sender)
{
	var parameters = {
		receiver : this_user, //the global variable
		sender : that_sender
	}
	$.getJSON(Flask.url_for("history"), parameters)
		.done(function(data){
			//console.log(data.message)
			console.log("successfully change the message data to read")
	})
		.fail(function(){
			console.log(errorThrown.toString());
		})
}


chooseForm = function(ele)
{
	$('.conversation').hide()
	$('#conversation_form').toggle('slide', 950)
	leave_city = $('#set_leave').text().trim()
	arrive_city = $('#set_arrive').text().trim()
	$('#flc').val(leave_city)
	$('#fac').val(arrive_city)
	$('#fu').val(this_user)
	$('#fed').val(my_text)
	//if cliked send to the flight, then set the #ff to the flight_number
	if (ele.id === "toflight")
	{
		$('#ff').val(flight_number)
		$('#broadcast_heading').text('Broadcast your request to this flight')
	}
	//if the id of the clicked element is toroute, clear the value. Thearitially,the id of this element shoud only be either toflight or toroute
	if (ele.id === "toroute")
	{
		$('#ff').val('')
		$('#broadcast_heading').text('Broadcast your request to this route')
	}
}


chooseUser = function(ele)
{
	var username = $('#'+ele.id).find('.name-meta').text().trim()
	if (username === 'All Passengers')
	{
		username = 'all'
	}
	var target_id = 'page_' + username
	if ((username !== 'all') && ($('#' + ele.id).find('.time-meta').text().trim() === 'message'))
	{
		$('#'+ele.id).find('.time-meta').text('online')
		check_history(username)//This is an ajax function. Query the data base and change the read_status of this message form 0 to 1
	}

	if ((username !== 'all') && ($('#' + ele.id).find('.time-meta').text().trim() === 'messages'))
	{
		$('#'+ele.id).find('.time-meta').text('offline')
		check_history(username)
	}

	if (username === 'all')
	{
		$('#sdid_all').find('.time-meta').text('')
		pchat_react() //it does not query the database but query the room_users dictionary all Roomuser(obj) and change the user's ifunread attribute to tell if this user has unread public message or not
	}
	$('.conversation').hide()// all the three static div on the right is hidden 
	$('#'+target_id).toggle('slide', 950)//the clikced section is slided to show on the right chatting panel
	$('#conversation_'+ username).scrollTop($('#conversation_' + username)[0].scrollHeight)
	user_state_change(username)
}


chooseEmoji = function(username)
{
	$('#comment_' + username).emojiPicker('toggle');
}

chooseUpload = function(ele, username)
{
	$('#comment_' + username).val('');
	var formData = new FormData();
	formData.append('image', ele.files[0])
	formData.append('fromuser', this_user)
	formData.append('touser', username)
	//console.log(formData)
	$.ajax({
		type:'POST',
		url: Flask.url_for('upload'),
		data: formData,
        contentType: false,
        cache: false,
        processData: false,
        async: true,
        success: function(data){
        	console.log(data)
        	//data = JSON.parse(data);
        	username = data.touser
        	img_url = data.img_url
        	img_content = "<a target='_blank' href = '" + img_url + "'><img class = 'chat_pic' src = '" + img_url + "' alt='send chat picture' /></a>"
        	$('#comment_' + username).val(img_content)
        	readytoSend(this,username)
        }
	})	
}


$(document).ready(function(e){

	var hey_user = this_user
	var welcome_title = hey_user + ' , Welcome to Flight ' + flight_number
	$('#toall_heading').text(welcome_title)

	//add emoji to the <select> -> <option> first static form.(boradcast to the flight / route form)
	var emonum_list = [127867,127843,128176,128176,128176,128140]
    var my_selector = document.getElementById('moneyamount')
    preemoji(my_selector, emonum_list)

    //client-side form validation. Can not be empty.Set this once the document is ready.
    $("#requesttext").attr('required', '');
    $("#email").attr('required', '');
    $("#moneyamount").attr('required', '');
})

//this function select the select tag and prepend emoji orderly loop through each option within the select tag 
function preemoji(selector, emonum_list)
{
    var i;
    var op_num = selector.length
    if (op_num !== emonum_list.length)
    {
        console.log('ERROR: The number of <options> in this select field does not match the length of emolist!')
        return false
    }
    for (i=0; i<op_num; i++)
    {
        var preemo = '&#' + emonum_list[i] + ';'
        selector.options[i].innerHTML = preemo + ' ' + selector.options[i].innerHTML
    }
}


readytoSend = function(ele, username)
{
	event.preventDefault()
	var finished_message = $('#comment_' + username).val()
	var to_user = username
	var from_user = this_user
	var belong_room = room_identifier
	var formatted_time = get_current_time()
	var sender_msg
	var tm_obj = $('#sdid_' + username).find('.time-meta')
	if (finished_message ===  "")
	{
		return false
	}
	$('#comment_' + username).val('').focus()
	$('#conversation_' + username).find('p').remove()
	if ((username !== 'all')&&(tm_obj.text().trim() === 'message'))
	{
		tm_obj.text('online')
		check_history(username)
	}

	if((username !== 'all')&&(tm_obj.text().trim() === 'messages')){
		tm_obj.text('offline')
		check_history(username)
	}

	if(to_user === 'all')
	{
		to_user = room_identifier
		tm_obj.text('')
		pchat_react()
	}
	socket.emit('my_event',{
		'msg': finished_message,
		'receiver_user': to_user,
		'sender_user': from_user,
		'room_name': belong_room
	})

    if (username !== 'all')
    {
	    sender_msg =         
		'<div class="row message-body">\
	      <div class="col-sm-12 message-main-sender">\
	        <div class="sender">\
	          <div class="message-text">' +
	            finished_message +
	          '</div>\
	          <span class="message-time pull-right">' +
	            formatted_time +
	          '</span>'+
	        '</div>\
	      </div>\
	    </div>'
    	$('#conversation_' + username).append(sender_msg)
    	$('#conversation_' + username).scrollTop($('#conversation_' + username)[0].scrollHeight)
    }
    user_state_change(username)
}

gotopro = function(browsename)
{
	var obj = {browsename : browsename};
	var url = Flask.url_for('myprofile') + "?" + $.param(obj)
	window.location.href = url
}


var socket = io.connect('https://' + document.domain + ':' + location.port);
//broadcast a message
socket.on("connect", function(){
	//alert('entering socketio connect method')
	console.log("clientside connection success")
	socket.emit("join", {"room_id": room_identifier, "status": "online"})

});



socket.on("handshake_response", function(msg){
	//alert('entering socketio handshake_response method')
	console.log(msg);
})

socket.on('join_response', function(msg){
	//alert('entering socketio join_response method')
	var new_d = new Date()
	// every and only client connected to this room should receive this message
	var joiner_obj = msg.joiner_obj  //json pickled string of this new joiner
	var room_users = msg.room_users	 //list containing all the pickled json object string in this specific room
	var unread_users = msg.unread_users  // list of this joiner containing all the username(not json pickled obj string) this joiner has received a unread message from
	var chat_history = msg.chat_history  // list of this joiner containing all the private messages (pickled json object string) related to this joiner
	var pchat_history = msg.pchat_history // list of this joiner containig all the public messages (pickled json object string) in this specific room
	joiner_obj = JSON.parse(joiner_obj)
	var joiner_obj_name = joiner_obj.username  //joiner_obj is Roomuser(obj), which is created on the server side and not saved in the backend database

	// initial joining the room? not currently in the room
	// because this join_response is sent to all every connected client, this is to check if this client is already in the mychat page or not.(has already joined the room or not//in other words, if this user is joiner or not)
	//CHECK IF THIS CLIENT IS THE JOINER HIMSELF(if it is the joiner himself, then doing the following)
	if($('#sdid_' + this_user).length <= 0)
	{
		if (joiner_obj.ifunread) //REMEMBER THE JOINER_OBJ IS ACTUALLY A ROOMUSER OBJ IN socketio.room_users. IT ALREADY CONTAINS THE CORRECT ifunread STATUS
		{
			$('#sdid_all').find('.time-meta').text('message')//always use user_state_change() method to update the left panel status bar. Because user_state_change() is based on the text change of time-meta
		}
		//this is related the status css in the left users panel.Give the username and find it in the left panel. Change the css according to the small text
		user_state_change('all')
		//no matter the joiner_obj has unread public message or not.use this method to show the public chat history
		//the below method only functioning when pchat_history has at least one record, or it will just be skipped
		add_pchat_history(pchat_history)
		//NOTICE THAT THE room_users.length is ensured to be at least one(the joiner himself. so be relaxed to loop through the list ^_^)
		for(var i=0; i<room_users.length; i++)
		{
			var each_obj = JSON.parse(room_users[i])
			var each_section  //used to construct each user's (of the joiner) left panel section. prepend it to the #online_section if this joiner has some unread message from that user in this room
			var the_msg
			// check if each username (each_obj (it is actually the Roomuser(obj) which has a username attribute)) is in the unread_users list (alist of username too)
			// if it is in the unread_users(a list of username), then change that user's time-meta in the left panel accroding to that user's status. message means that that user is currently online while messages mesans that user is currently offline
			if (jQuery.inArray(each_obj.username, unread_users) > -1)
			{
				if (each_obj.status === 'online'){
					the_msg = 'message'
				}
				else if(each_obj.status === 'offline'){
					the_msg = 'messages'
				}
				else
				{
					console.log("error occured in join_response method. Theratically, each_obj(Roomuser(obj)'s status should either be online or offline, not anything else_1")
				}
				each_section = '<div class="sideBar-body" onclick = "chooseUser(this)" id = "sdid_' + each_obj.username + '"><div class="col-sm-3 col-xs-3 sideBar-avatar"><div class="avatar-icon"><img src="https://s3-ap-northeast-1.amazonaws.com/pandajet/' + each_obj.userid + '_pf.png?' + new_d.getTime() +'"></div></div><div class="col-sm-9 col-xs-9 sideBar-main"><div class="row"><div class="col-sm-8 col-xs-8 sideBar-name"><span class="name-meta">' + each_obj.username + '</span></div><div class="col-sm-4 col-xs-4 pull-right sideBar-time"><span class="time-meta pull-right blink_me">' + the_msg + '</span></div></div></div></div>'
            	$("#online_section").prepend(each_section)  //potential problem here.
			}
			// IF THAT USER'S USERNAME IS NOT IN THE UNREAD LIST
			else
			{
				each_section = '<div class="sideBar-body" onclick = "chooseUser(this)" id = "sdid_' + each_obj.username + '"><div class="col-sm-3 col-xs-3 sideBar-avatar"><div class="avatar-icon"><img src="https://s3-ap-northeast-1.amazonaws.com/pandajet/' + each_obj.userid + '_pf.png?' + new_d.getTime() + '"></div></div><div class="col-sm-9 col-xs-9 sideBar-main"><div class="row"><div class="col-sm-8 col-xs-8 sideBar-name"><span class="name-meta">' + each_obj.username + '</span></div><div class="col-sm-4 col-xs-4 pull-right sideBar-time"><span class="time-meta pull-right">' + each_obj.status + '</span></div></div></div></div>'
				if (each_obj.status === 'online')
				{
					$('#online_section').append(each_section)
				}
				else if (each_obj.status === 'offline')
				{
					$('#offline_section').append(each_section)
				}
				else
				{
					console.log("error occured in join_response method. Theratically, each_obj(Roomuser(obj)'s status should either be online or offline, not anything else_2")
				}
			}
			add_right_page(each_obj)
			add_chat_history(chat_history)
			user_state_change(each_obj.username)
		}
		// hide this user in the left section
		$('#sdid_' + this_user).hide()
		//only need to add this emojiPicker to the #comment_all tag. Because if this client is not the joiner, then it must already called this when he first join the room as the joiner
		$("#comment_all").emojiPicker({
			width: '200px',
			height: '180px',
			button: false
		});
	}
	//if the client is currently in the room.(in other words, if this client is not the joiner)
	else
	{
		//if the joiner(not this client) is new(totally new to this room,) and have not got any records(in the left panel or in other words in the room_users dictionary you can not find this joiner) before
		if ($('#sdid_' + joiner_obj_name).length <= 0)
		{
			var each_section = '<div class="sideBar-body" onclick = "chooseUser(this)" id = "sdid_' + joiner_obj_name + '"' + '><div class="col-sm-3 col-xs-3 sideBar-avatar"><div class="avatar-icon"><img src="https://s3-ap-northeast-1.amazonaws.com/pandajet/' + joiner_obj.userid + '_pf.png?' + new_d.getTime() + '"></div></div><div class="col-sm-9 col-xs-9 sideBar-main"><div class="row"><div class="col-sm-8 col-xs-8 sideBar-name"><span class="name-meta">' + joiner_obj_name+ '</span></div><div class="col-sm-4 col-xs-4 pull-right sideBar-time"><span class="time-meta pull-right">' + joiner_obj.status+ '</span></div></div></div></div>'
            $('#online_section').append(each_section)
            //do not need to loop through each user in this room to add the right page.Just add the new joiner's right page is fine
            add_right_page(joiner_obj)
		}
		// if the joiner is not new and thus not the first time joined this room. You can find the records of him in the left panel and the room_users
		// here, the status of this joiner should only be either offline or messages(have unread message from this joiner). How can online user join the room?
		else
		{
			if ($('#sdid_' + joiner_obj_name).find('.time-meta').text().trim() === 'offline')
			{
				$('#sdid_' + joiner_obj_name).find('.time-meta').text(joiner_obj.status)
			}
			else if ($('#sdid_' + joiner_obj_name).find('.time-meta').text().trim() === 'messages')
			{
				$('#sdid_' + joiner_obj_name).find('.time-meta').text('message')
			}
			else
			{
				console.log("the status of this joiner should only be either offline or messages(have unread message from this joiner). How can online user join the room?")
			}
			//the following code are basically changing the position of the user on the left panel
			//I already cooperated the following code to the user_state_change function
			//var reenter_div = $('#sdid_' + joiner_obj_name).get(0)
			//$('#sdid' + joiner_obj_name).remove()
			//$('#online_section').append(reenter_div)
		}
		// since this client is already inthe room.so no need to loop every that user, but only need to update the time-meta status of the new joiner
		user_state_change(joiner_obj_name)
	}
})


socket.on('normal_response', function(msg){
	var receiver_user = msg.receiver_user
	var sender_user = msg.sender_user
	var room_name = msg.room_name
	var the_message = msg.msg
	var now = new Date(Date.now())
	var formatted_time = get_current_time();
	if (receiver_user === room_name)
	{
		receiver_user = 'all'
	}
	// check if this message is sent to all or just this user
	//if receiver_user === this_user equals to true, then it means this message is sent to this client only not to all the clients in this room
	if (receiver_user === this_user)
	{
		$('#sdid_' + sender_user).find('.time-meta').text('message')
		user_state_change(sender_user)
	}
	if (receiver_user === 'all')
	{
		// to check if it is this client that emits the message to all passengers
		// if sender_user !== this_user equals to true, then it means this client is not the one who emits the public message
		if (sender_user !== this_user)
		{
			$('#sdid_all').find('.time-meta').text('message')
			user_state_change('all')
		}
		$('#conversation_all').find('p').remove()
		var receiver_msg = '<div class="public_talk"><div class="public_sender">' + sender_user + '</div><div class="public_msg">' + the_message + '</div><span class="message-time pull-right">' + formatted_time + '</span><div class="clear_div"></div></div>'
		$('#conversation_all').append(receiver_msg)
		$('#conversation_all').scrollTop($('#conversation_all')[0].scrollHeight)
	}
	// if receiver_user is not all, which means this should be a private instead of a public message
	else
	{
		$('#conversation_' + sender_user).find('p').remove()
		var receiver_msg = '\
		<div class="row message-body">\
          <div class="col-sm-12 message-main-receiver">\
            <div class="receiver">\
              <div class="message-text">' +
               the_message +
              '</div>\
              <span class="message-time pull-right">' +
                formatted_time +
              '</span>\
            </div>\
          </div>\
        </div>'
    	$('#conversation_' + sender_user).append(receiver_msg)
    	// even though the code below is called in the chooseUser function. But we add it here in case this client who receives the message from the sender_user keeps in the same chatting page.
    	// If we add the code below, the page will automatically scroll to the bottom without the message receiver client needing to click the chooseUser button/or scroll manually to see the latest message
    	$('#conversation_'+ sender_user).scrollTop($('#conversation_' + sender_user)[0].scrollHeight)
	}
})



socket.on('disconnect_response', function(msg)
{
	var leaving_user_obj = msg.leaving_user_obj;
	leaving_user_obj = JSON.parse(leaving_user_obj);
	var leaving_user_name = leaving_user_obj.username;
	var text_obj = $('#sdid_' + leaving_user_name).find('.time-meta');
	if (text_obj.text().trim() === 'online')
	{
		text_obj.text('offline')
	}
	else if (text_obj.text().trim() === 'message')
	{
		text_obj.text('messages')
	} 
	else
	{
		console.log("ERROR!: one disconnect user status bar is neither online or message<function:disconnect_response socket>")
	}
	//var leave_div = $('#sdid_' + leaving_user_name).get(0)
	//$('#sdid_' + leaving_user_name).remove()
	//$('#offline_section').append(leave_div)
	user_state_change(leaving_user_name)

})




