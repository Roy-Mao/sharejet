var $uploadCrop;
var this_user = $("#from_user").text().trim()
var userid = $('#hiddenid').text().trim()
//var have_pic = $('#have_;pic').text().trim()

function readFile(input, crop)
{
    if (input.files && input.files[0]) 
    {
        var reader = new FileReader();          
        reader.onload = function (e) 
        {
            result = e.target.result;
            arrTarget = result.split(';');
            tipo = arrTarget[0];
            if (tipo == 'data:image/jpeg' || tipo == 'data:image/png') 
            {
                crop.croppie('bind', 
                {
                    url: e.target.result
                });
            } 
            else 
            {
                alert('Error: Accept only .jpg o .png image types');
                return false
            }
        }           
        reader.readAsDataURL(input.files[0]);
		return true
    }
    else
    {
    	return false
    }
}

$(document).ready(function()
{
	//alert(userid)
	var d = new Date()
	//$('.profile-pic').css('background-image', 'url(/static/img/proimg/' + userid + '_pf.png?' + d.getTime() + ')');
	$('.profile-pic').css('background-image', 'url(https://s3-ap-northeast-1.amazonaws.com/pandajet/' + userid + '_pf.png?' + d.getTime() + ')');		
	//$('.profile-pic-browse').css('background-image', 'url(/static/img/proimg/' + userid + '_pf.png?' + d.getTime() + ')');
	$('.profile-pic-browse').css('background-image', 'url(https://s3-ap-northeast-1.amazonaws.com/pandajet' + userid + '_pf.png?' + d.getTime() + ')');
	$('#user_pic').change(function()
		{
			$('#change_div').empty()
			$uploadCrop = $('#change_div').croppie({
				//enableExif: true,
				viewport: 
				{
					width: 80,
					height: 80,
					type: 'circle'
				},
				boundary: 
				{
					width: 150,
					height: 150
				},
				showZoomer: false
				});

			read_status = readFile(this, $uploadCrop);
			if (read_status)
			{
			    $('#pic_div').hide()
				$('#outer_change').show()
				$changediv = $('#change_div').find('.cr-boundary')
				$changediv.attr('data-toggle', 'tooltip');
				$changediv.attr('data-placement', 'right');
				$changediv.attr('title', 'Zoom to resize');
				$changediv.tooltip()
				cnbtn = function(ele)
				{
					$uploadCrop.croppie('result', {type: 'base64', size: {width:300, height:300}, circle: true, quality:1}).then(function(resp){
						//console.log('ready to enter transmission')

						$.ajax({
							url: Flask.url_for("propic"),
							data: JSON.stringify({"picstring": resp, "this_user": this_user}),
							contentType: "application/json; charset=utf-8",
							type: "POST",
							dataType: "json",
							cache: false,
							processData: false,
							async: true
							})
							.done(function(data)
							{
								swal("Success!", "You have successfully updated your profile picture.", "success");
								$uploadCrop.croppie('destroy')
								$('.profile-pic').css('background-image', 'url(' + resp + ')');
								$('#pic_div').show()
								$('#outer_change').hide()
	        				})
	        				.fail(function(xhr, textStatus, errorThrown)
	        				{
	        					//console.log("ERROR: ajax request failed. <cnbtn function client side>")
	        					console.log(xhr.statusText);
	        					console.log(textStatus);
	        					console.log(errorThrown);
	        					$uploadCrop.croppie('destroy')
	        				})
					})
				}
				babtn = function(ele)
				{
					$uploadCrop.croppie('destroy')
					$('#pic_div').show()
					$('#outer_change').hide()
					$('#user_pic').val('')	
				}
			}
			else
			{
				console.log('ERROR: can not read or write the file or no file input')
			}
			
		});
	});





