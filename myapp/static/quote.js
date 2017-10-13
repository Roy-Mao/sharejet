
//Notice: basically this javascript only has relation to the quote.html.
//It does two basic things: 1.add the datepicker plug-in. 2.add twitter typeahead search functionality
// two jquery plugins need to avoid confliction.
var datepicker = $.fn.datepicker.noConflict(); 
$.fn.bootstrapDP = datepicker;
// avoid confliction setting 

$(function(){

    var emonum_list = [127867,127843,128176,128176,128176,128140]
    var my_selector = document.getElementById('moneyamount')
    preemoji(my_selector, emonum_list)

    // datepicker plug-in settings
    $('.datepicker').bootstrapDP({
        startDate: '-2d'
    });

    // typeahead plug-in settings
	$(".q").typeahead({
		highlight: true,
		hint: true,
		minLength: 1
	},
	{
		display: 'airport_name',
        limit: 10,
        source: search,
        templates: {
        	notFound: "<div> not matches found</div>",
            suggestion: Handlebars.compile(
            	"<div>" +
            	"{{airport_name}} - {{city}}" +
            	" </div>"
            )
        }
	});

    //quote form clear and reset. Two form only submit one, click one form will clear the typed in data in the other form
    $("#headingOne").click(function()
    {
        $("#collapseTwo .errors").remove();
        $("#flightnumber").attr('required', '');
        $("#requesttext").removeAttr('required');
        $("#requesttext").val('');
        $("#moneyamount").val('');
        $('#moneyamount').removeAttr('required');
        $("#contact").removeAttr('required');
        $("#contact").val('');
    }
    );

    $("#headingTwo").click(function()
    {
        $("#collapseOne .errors").remove();
        $("#flightnumber").removeAttr('required');
        $("#requesttext").attr('required', '');
        $('#moneyamount').attr('required', '')
        $("#contact").attr('required', '');
        $("#flightnumber").val('');
    }
    );


    if ($("#collapseOne .errors").length > 0)
    {
        $("#collapseOne").addClass("in");
        $("#collapseOne").attr('aria-expanded', 'true');
    };

    if ($("#collapseTwo .errors").length > 0)
    {
        $("#collapseTwo").addClass("in");
        $("#collapseTwo").attr('aria-expanded', 'true')
    };
})


function search(query, syncResults, asyncResults)
{
    // get places matching query (asynchronously)
    var parameters = {
        q: query
    };
    $.getJSON(Flask.url_for("search"), parameters)
    .done(function(data, textStatus, jqXHR) {
     
        // call typeahead's callback with search results (i.e., places)
        asyncResults(data);
    })
    .fail(function(jqXHR, textStatus, errorThrown) {

        // log error to browser's console
        console.log(errorThrown.toString());

        // call typeahead's callback with no results
        asyncResults([]);
    });
}

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
