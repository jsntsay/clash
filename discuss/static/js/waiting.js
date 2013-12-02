$( window ).load(function() {
	var $waiting = $("#waiting");
	var baseMessage = $waiting.text();
	if ($waiting.length > 0) {
		var max = 5;
		var current = 0;
		window.setInterval(function() {
			var message = baseMessage;
			for (var i = 0; i < current; i++) {
				message = message + ".";
			}
			current++;
			if (current > max)
				current = 0;
			$waiting.text(message);
		}, 750);
	}
});