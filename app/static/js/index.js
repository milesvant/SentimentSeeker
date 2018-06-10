// Submit form on 'enter' while preventing it from showing on the form
$(document).keypress(
	function(event){
        	if (event.which == '13') {
          		event.preventDefault()
          		document.getElementById("submit-btn").click();
}});
