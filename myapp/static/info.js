$(document).ready(function()
{
	//Try to initialize all tooltips on a page by their data-toggle attribute
	$(function () 
	{
		$('[data-toggle="tooltip"]').tooltip()
	}
	);

	d = new Date()
	var userid = $("#info_hiddenid").text().trim()
	//document.getElementById('info_pp_img').src = "./static/img/proimg/" + userid + "_pf.png?" + d.getTime();
	document.getElementById('info_pp_img').src = "https://s3-ap-northeast-1.amazonaws.com/pandajet/" + userid + "_pf.png?" + d.getTime();

	$('.ajax_a').editable({
		mode: 'inline',
		validate: function(value) 
		{
			if($.trim(value) == '') 
			{
				//alert('fddafda')
				return 'This field is required';
			}
		},

		success: function(response, newValue)
		{
			console.log(response.success)
			if(!response.success)
			{
				console.log('Error, the an ajax call response is not successfully returned.')
				return false	
			}
		}
	});

	$('.ajax_b').editable({
		escape: false,
		value: ' ',
		source:
		[
			{value:' ', text:'Options'},
			{value:'<i class="em em-beers"></i> I can offer a hug and a beer', text:'Hug and Beer'},
			{value:'<i class="em em-sushi"></i> Let me grab you some food and have a nice talk', text: 'Smile and Food'},
			{value:'<i class="em em-moneybag"></i> $0 - $15', text:'$0 - $15'},
			{value:'<i class="em em-moneybag"></i> $16 - $40', text:'$16 - $40'},
			{value:'<i class="em em-moneybag"></i> above $40', text:'above $40'},
			{value:'<i class="em em-love_letter"></i> Contact me for details', text:'Other'}

		],

		validate: function(value) 
		{
			if($.trim(value) == '') 
			{
				return 'Choose one.';
			}
		},

		success: function(response, newValue)
		{
			if(!response.success)
			{
				console.log('Error, the an ajax call response is not successfully returned.')
				return false	
			}
			//because I can not add the emoji before the option text. using escape method provided by the x-editable plug-in can not render the html in the dropmenu
			//although it can be shown after you choose the option.
			//so I decided to reload the page to show everything correctly.
			location.reload()
		}
	});

});





removeRow = function(el, info_id, oot)
{
	var request_data = {
		request_id: info_id,
		request_oot: oot
	};

	swal({
		title: "Sure to delete?",
		text: "No one would see your request if deleted.",
		type: "warning",
		showCancelButton: true,
		confirmButtonColor: "#d33",
		confirmButtonText: "Yes, delete it!",
		closeOnConfirm: false
	},
	function(){
		$(el).parents("tr").fadeOut(550, function(){
			if ($(el).parents("tr").hasClass("accordion-toggle"))
			{
				$(el).parents("tr").next("tr").remove()
			}
			$(el).parent("tr").remove()       
			})

			$.getJSON(Flask.url_for("index"), request_data)
			.done(function(data, textStatus, jqXHR){
				swal("Deleted!", data.message, "success");
			})
			.fail(function( jqxhr, textStatus, error ) {
    			var err = textStatus + ", " + error;
    			console.log( "Request Failed: " + err);
			});
			}
	);
}


sendtemail = function(el)
{
	swal({
		title: "One click help",
		text: "Sure about sending a contact email to this user?",
		type: "info",
		showCancelButton: true,
		confirmButtonColor: "#538ae2",
		confirmButtonText: "Yes, confirm!",
		closeOnConfirm: false,
		showLoaderOnConfirm: true,
	},
	function(){
		$(el).closest("form").submit();
		//swal({title:"Your help is sweet!", text:"A contact email has been sent. This user will contact you via your email directly.", timer:3000, imageUrl:"/static/img/thumb_up.jpg", showConfirmButton: false})
		setTimeout(function()
			{
				swal("Success! Thank you for the help.");
			}, 5000);
			
	});
}

var options = {expires: 1};
if ($.cookie('visits') == null)
{
  starttour();
  $.cookie('visits', '1', options);
}










