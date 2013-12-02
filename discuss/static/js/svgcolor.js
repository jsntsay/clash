$( window ).load(function() {
	var $avatar = $(".avatar");
	if ($avatar.length > 0) {
		$avatar.each(function() {
			var color = $(this).attr("color");
			if (color != null) {
				var svgDoc = $(this)[0].contentDocument;
				var elements = (svgDoc.getElementsByClassName("fillcolor"));
				for (var i = 0; i < elements.length; i++) {
					elements[i].setAttribute("fill", color);
				}
			}
		});
	}
});