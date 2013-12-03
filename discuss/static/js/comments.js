// ajax function for updating free talk during submission and periodically
$( document ).ready(function() {
	
	// brittle way of getting the discussid from the url
	var pathname = window.location.pathname;
	var split = pathname.split("/");
	var discussid = split[2];

	function checkComments() {
		$.get( "/comments/" + discussid, function(xml) {
			var $commentdiv = $("div#comments")
			$commentdiv.empty();
			$(xml).find("comment").each(function( index, element ) {
				var text = $(this).find('text').text();
				var usertype = $(this).find('usertype').text();
				var time = $(this).find('time').text();
				if (usertype == "a") {
					var $newcomment = $( '<div class="bubbleA"> ' + text + ' </div> <p class="timeA"> ' + time + " </p>")
					$newcomment.appendTo($commentdiv);
				}
				else if (usertype == "b") {
					var $newcomment = $( '<div class="bubbleB"> ' + text + ' </div> <p class="timeB"> ' + time + " </p>")
					$newcomment.appendTo($commentdiv);
				}
			});
		});
	}
	
	$("input[type='submit']").click(function(event) {
		event.preventDefault();
		var csrftoken = $.cookie('csrftoken');
		var $textinput = $("textarea")
		var textvalue = $textinput.val();
		$textinput.val("");
		$.post( "/comments/" + discussid, {csrfmiddlewaretoken:csrftoken,currentstate:'free',text:textvalue}, function(xml) {
			var $commentdiv = $("div#comments");
			$commentdiv.empty();
			$(xml).find("comment").each(function( index, element ) {
				var text = $(this).find('text').text();
				var usertype = $(this).find('usertype').text();
				var time = $(this).find('time').text();
				if (usertype == "a") {
					var $newcomment = $( '<div class="bubbleA"> ' + text + ' </div> <p class="timeA"> ' + time + " </p>")
					$newcomment.appendTo($commentdiv);
				}
				else if (usertype == "b") {
					var $newcomment = $( '<div class="bubbleB"> ' + text + ' </div> <p class="timeB"> ' + time + " </p>")
					$newcomment.appendTo($commentdiv);
				}
			});
		});
		
		// hide encouragement message if it exists after posting a message
		var $finishmsg = $("div#finishmessage");
		if ($finishmsg.length > 0) {
			$finishmsg.hide();
		}
	});
	
	//window.setInterval(checkComments, 500);
	
});
