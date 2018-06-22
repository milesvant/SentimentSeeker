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