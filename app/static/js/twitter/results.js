// Display each tweet using Twitter's embedding API
 window.onload = (function() {
   $(".tweet").each(function() {
     var id = $(this).attr("tweetID");
     console.log(id);
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