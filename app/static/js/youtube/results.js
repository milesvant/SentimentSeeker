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
    let query = window.location.href.split("/results/")[1];
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
        if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
            if ('videos' in data) {
                // if done show videos
                show_videos(data['videos']);
            }
            else {
                // something unexpected happened
                $(status_div.childNodes[3]).text('Result: ' + data['state']);
            }
        }
        else {
            // rerun in 2 seconds
            setTimeout(function() {
                update_progress(status_url, nanobar, status_div);
            }, 2000);
        }
    });
}

function show_videos(videos) {
  // hide progress bar
  $("#progress").hide()
  // add each video to its respective area of the page
  for (let i = 0; i < videos.length; i++) {
    let vid = videos[i]
    if (vid['score'] <= 0) {
      console.log("negative");
      let negative_entry = `<table class="table">
              <tr>
                <td width="50px">
                      <span class="glyphicon glyphicon-thumbs-down"></span>
                </td>
                  <td>
                     <a href="https://www.youtube.com/watch?v=${ vid['videoid'] }">${ vid['title'] }</a>
                  </td>
              </tr>
      </table>`;
      $('#negatives').append(negative_entry);
    } else {
      console.log("positive");
      let positive_entry = `<table class="table">
              <tr>
                <td width="50px">
                      <span class="glyphicon glyphicon-thumbs-up"></span>
                </td>
                  <td>
                     <a href="https://www.youtube.com/watch?v=${ vid['videoid'] }">${ vid['title'] }</a>
                  </td>
              </tr>
      </table>`;
      $('#positives').append(positive_entry);
    }
  }
}

// Run start_download upon page loading
$(document).ready(start_download());
