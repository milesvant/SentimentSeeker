// Display each tweet using Twitter's embedding API
 window.onload = (function() {
   $(".tweet").each(function() {
     var id = $(this).attr("tweetID");
     twttr.widgets.createTweet(
       id, this,
       {
         conversation : 'none',    // or all
         cards        : 'hidden',  // or visible
         linkColor    : '#cc0000', // default is blue
         theme        : 'light'    // or dark
       });
   });
 });

 // Submit twitter search form on 'enter' while preventing it from showing on the form
 $('#twitter-form').keypress(
 	function(event){
         	if (event.which == '13') {
           		event.preventDefault()
           		document.getElementById("twitter-submit-btn").click();
 }});

// Fill in search bar with current query as placeholder
 $('#search-box').attr("placeholder", decodeURI(window.location.href.split("/twitter_results/")[1]));

 function display_failure_overlay() {
   // Unhide the error message overlay
   var query = window.location.href.split("/twitter_results/")[1];
   var overlay_message = `<p>There was an unexpected internal error.</p><br>
                          <a href="/twitter_results/${ query }" style="color:#FF7466;">Try Again</a>
                          <br><a href="/" style="color:#FF7466;">Home</a>`;
   $('#overlay-text').append(overlay_message);
   $('#overlay').css('visibility', 'visible');
   $('#overlay-text').css('visibility', 'visible');
 }
