// ajax function for refreshing the page if partner is done
$( document ).ready(function() {

	// brittle way of getting the discussid from the url
	var pathname = window.location.pathname;
	var split = pathname.split("/");
	var discussid = split[2];
	
	function check() {
		$.get( "/contextcheck/" + discussid, function(xml) {
			var done = $(xml).find("done").text();
			if (done == "1") {
				setTimeout(function() {
					location.reload(true);
				}, 500);
			}
		});
	}
	
	window.setInterval(check, 500);
});