$( document ).ready(function() {
	$(".infoboxsmall").click( function() {
		var checked = $(this).find('input[type="radio"]')[0].checked;
		
		if (checked == false)
			$(this).find('input[type="radio"]')[0].checked = true;
		else
			$(this).find('input[type="radio"]')[0].checked = false;
		
		$(".infoboxsmall").each( function() {
			if ($(this).find('input[type="radio"]')[0].checked == true) {
				$(this).addClass('selectedinfobox');
			}
			else {
				$(this).removeClass('selectedinfobox');
			}
		});
	});
});