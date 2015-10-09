/***
 * This contains all of the JavaScript required for our minimal CATAN interface.
 */

/**
 * Simple function to get the location of the device accessing the website
 * 
 * Ref: http://www.w3schools.com/html/html5_geolocation.asp
 */
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(updateLocation);
    }
}

/**
 * Asynchronous callback for getting position (May require user prompt)
 * 
 * @param position Object containing position information.
 */
function updateLocation(position) {
	
	field = document.getElementById("geo_location");
	
	if (field) {
		pos = position.coords.latitude +
		"," + position.coords.longitude+
		","+ position.coords.accuracy;
		
		field.setAttribute("value",pos);
	}
	
//	// Display this to the user
//	pos_vis = "Detected (Accuracy: "+ position.coords.accuracy+"m)";
//	visible = document.getElementById("geo_location_visible");
//	visible.removeChild(visible.firstChild);
//	visible.appendChild(document.createTextNode(pos_vis));
}



//callback handler for form submit
$('#registrationform').submit(function(e)
{
	
	e.preventDefault(); //STOP default action
	$('input:submit').attr("disabled", true);	
	
	// Extract our form data
    var postData = $(this).serializeArray();
    var formURL = $(this).attr("action");
    
    
    requirements_met = true;
    // Loop over all of our inputs to ensure that they are populated
    $.each(postData, function(i, field) {
    	var input = $('[name='+field.name+']');
    	field.value = $.trim(field.value);
    	
    	// Ignore certain fields
    	if (field.name == "submitter_gps") {
    		return;
    	}
    	
    	// If the value isn't set, highlight the field red
    	if (field.value == "" || !field.value) {
    		input.attr("class","highlight_input");
    		requirements_met = false;
    	} else {
    		input.removeAttr("class");
    	}
    	
    	// Validate fields
    	if (field.name == "age") {
    	   if (!$.isNumeric(field.value)) {
    	       alert('Age must be a number.');
    	       requirements_met = false;
    	   }
    	}
    })
   
    // Are all of the fields filled in?
    if (!requirements_met) {
    	$('input:submit').attr("disabled", false);
    	return;
    }
    
    // Make our AJAX request
    $.ajax(
    {
        url : formURL,
        type: "POST",
        data: new FormData( this ),
        processData: false,
        contentType: false,
        success:function(data, textStatus, jqXHR) 
        {
            if (data == 0) {
                alert('Update failed.  Please try again later.');
            } else {
                search_loc = String(window.location);
                search_loc = search_loc.replace("new_person","profile/"+data);
                window.location = search_loc;
            }
            //data: return data from server
        },
        error: function(jqXHR, textStatus, errorThrown) 
        {
        	alert("Failed creating new person.  Try again later.");
            //if fails      
        }
    });
    e.preventDefault(); //STOP default action
    
    
});


$('.profile_form').submit(function(e)
		{
			e.preventDefault(); //STOP default action
			$('input:submit').attr("disabled", true);	
			
			// Extract our form data
		    var formURL = $(this).attr("action");
		    
		    $.ajax( {
		        url: formURL,
		        type: 'POST',
		        data: new FormData( this ),
		        processData: false,
		        contentType: false,
		        success:function(data, textStatus, jqXHR) 
		        {
		        	$('input:submit').attr("disabled", false);
		        	if (data == 0) {
		        	 alert('Update failed.  Please try again later.');
		        	} else {
		        	 location.reload();
		        	}
		            //data: return data from server
		        },
		        error: function(jqXHR, textStatus, errorThrown) 
		        {
		            //if fails
		        	alert('Update failed.  Please try again later.');
		        	
		        	$('input:submit').attr("disabled", false);	
		        }
		      } );
		    
		    
		    
		});

$('.identify_form').submit(function(e)
		{
			e.preventDefault(); //STOP default action
			$('input:submit').attr("disabled", true);	
			
			// Extract our form data
		    var formURL = $(this).attr("action");
		    
		    $.ajax( {
		        url: formURL,
		        type: 'POST',
		        data: new FormData( this ),
		        processData: false,
		        contentType: false,
		        success:function(data, textStatus, jqXHR) 
		        {
		        	$('input:submit').attr("disabled", false);
		        	if (data == 0) {
		        	 alert('Update failed.  Please try again later.');
		        	} else {
		        	 location.reload();
		        	}
		            //data: return data from server
		        },
		        error: function(jqXHR, textStatus, errorThrown) 
		        {
		            //if fails
		        	alert('Update failed.  Please try again later.');
		        	
		        	$('input:submit').attr("disabled", false);	
		        }
		      } );
		    
		    
		    
		});


$('.services_form').submit(function(e)
		{
			e.preventDefault(); //STOP default action
			$('input:submit').attr("disabled", true);

			// Extract our form data
		    var formURL = $(this).attr("action");

			data = new FormData( this );

		    $.ajax( {
		        url: formURL,
		        type: 'POST',
		        data: data,
		        processData: false,
		        contentType: false,
		        success:function(data, textStatus, jqXHR)
		        {
		        	$('input:submit').attr("disabled", false);
		        	if (data == 0) {
		        	 alert('Update failed.  Please try again later.');
		        	} else {
		        	 location.reload();
		        	}
		            //data: return data from server
		        },
		        error: function(jqXHR, textStatus, errorThrown)
		        {
		            //if fails
		        	alert('Update failed.  Please try again later.');

		        	$('input:submit').attr("disabled", false);
		        }
		      } );



		});


// Make our table rows clickable
jQuery(document).ready(function($) {
    $(".clickableRow").click(function() {
          window.document.location = $(this).attr("href");
    });
    $("#header").click(function() {
        window.document.location = "?";
  });
});
//$(".clickableRow").mouseover(function() {
//	$(this).removeClass("clickableRow");
//	$(this).addClass("clickableRowHover");
//})
 
//$("#registrationform").submit(); //Submit  the FORM

function requestService(service_type, service_subtype, request_text) {

	var service_comments = prompt(request_text+"\nAny additional " +
	"comments?");

	// Did they cancel it?
	if (service_comments == null) {
		return;
	}


	// Fill in our form data
	form_data = new FormData();
	form_data.append("service_type", service_type);
	form_data.append("service_subtype", service_subtype);
	form_data.append("service_comments", service_comments);
	form_data.append("service_status", 0); // 0 - SUBMITTED

	submitter_gps = $('#geo_location').attr('value');
	form_data.append("submitter_gps", submitter_gps);

	$.ajax( {
		url: '/service_submit',
		type: 'POST',
		data: form_data,
		processData: false,
		contentType: false,
		success:function(data, textStatus, jqXHR)
		{
			//data: return data from server
			if (data == "0") {
				alert("ERROR: Could not submit request.  Please try again " +
				"later.");
			} else {
				location.reload()
			}
		},
		error: function(jqXHR, textStatus, errorThrown)
		{
			//if fails
			alert('Request failed.  Please try again later.');
		}
	} );
}