// Run start_download upon page loading
$(document).ready(start_download());
// Holds a list of the videoids of the videos which have been displayed already
var visible_videos = [];

function start_download() {
    // add task status elements
    div = $('<div class="progress"><div></div><div>0%</div><div>...</div><div>&nbsp;</div></div><hr>');
    $('#progress').append(div);

    // create a progress bar
    var nanobar = new Nanobar({
        bg: '#44f',
        target: div[0].childNodes[0]
    });

    // send ajax POST request to start background job
    var query = window.location.href.split("/results/")[1];
    $.ajax({
        type: 'POST',
        url: `/download/${query}`,
        success: function(data, status, request) {
            status_url = request.getResponseHeader('Location');
            update_progress(status_url, nanobar, div[0]);
        },
        error: function() {
            alert('Unexpected error');
        }
    });
}

function update_progress(status_url, nanobar, status_div) {
    // send GET request to status URL
    $.getJSON(status_url, function(data) {
        // update UI
        percent = parseInt(data['current'] * 100 / data['total']);
        nanobar.go(percent);
        $(status_div.childNodes[1]).text(percent + '%');
        $(status_div.childNodes[2]).text(data['status']);
        console.log(data);
        if (data['state'] == 'FAILED' || data['state'] == 'DONE') {
            if ('videos' in data) {
                // hide progress bar
                $("#progress").hide()
                // if done show videos
                show_videos(data['videos']);
            }
            else if (data['state'] == 'FAILED') {
                // upon failure hide the progress bar and display a failure
                // message overlay
                $("#progress").hide();
                display_failure_overlay();
            } else {
                // something unexpected happened
                $(status_div.childNodes[3]).text('Result: ' + data['state']);
            }
        }
        else {
          if ('videos' in data) {
              show_videos(data['videos']);
          }
          // rerun in 2 seconds
          setTimeout(function() {
                update_progress(status_url, nanobar, status_div);
          }, 2000);
        }
    });
}

function show_videos(videos) {
  // add each video to its respective area of the page
  for (let i = 0; i < videos.length; i++) {
    display_video(videos[i]);
  }
}

function display_video(video) {
  // Displays video results in their respective columns after checking if they
  // have already been displayed
  if (visible_videos.includes(video['videoid'])) {
    return;
  }
  if (video['score'] <= 0) {
    // negatives
    var negative_entry = `<table class="table">
            <tr>
              <td width="50px">
                    <span class="glyphicon glyphicon-thumbs-down"></span>
              </td>
                <td>
                   <a href="https://www.youtube.com/watch?v=${ video['videoid'] }">${ video['title'] }</a>
                </td>
            </tr>
    </table>`;
    $('#negatives').append(negative_entry);
  } else {
    // positives
    var positive_entry = `<table class="table">
            <tr>
              <td width="50px">
                    <span class="glyphicon glyphicon-thumbs-up"></span>
              </td>
                <td>
                   <a href="https://www.youtube.com/watch?v=${ video['videoid'] }">${ video['title'] }</a>
                </td>
            </tr>
    </table>`;
    $('#positives').append(positive_entry);
  }
  visible_videos.push(video['videoid']);
}


function display_failure_overlay() {
  // Unhide the error message overlay
  var query = window.location.href.split("/results/")[1];
  var overlay_message = `<p>There was an unexpected internal error.</p><br>
                         <a href="/results/${ query }" style="color:#FF7466;">Try Again</a>
                         <br><a href="/" style="color:#FF7466;">Home</a>`;
  $('#overlay-text').append(overlay_message);
  $('#overlay').css('visibility', 'visible');
  $('#overlay-text').css('visibility', 'visible');
}
