// Submit youtube form on 'enter' while preventing it from showing on the form
$('#youtube-form').keypress(
	function(event){
        	if (event.which == '13') {
          		event.preventDefault()
          		document.getElementById("youtube-submit-btn").click();
}});

// Submit twitter form on 'enter' while preventing it from showing on the form
$('#twitter-form').keypress(
	function(event){
        	if (event.which == '13') {
							console.log("twitter");
          		event.preventDefault()
          		document.getElementById("twitter-submit-btn").click();
}});