$(document).ready(function() {
    vote.init();
});

var vote = {
  url: '/vote/',
  moodId:     null,
  moodPairId: null,
  
  init: function() {
    
    vote.loadPair();
  },

  loadPair: function() {
    $.get('/displayMoodPair', {}, function(data) {
      $('#moods').html(data);
      vote.listen();
      vote.loadStats();
    });
  },


  listen: function() {
    $('.moodlink').click( function() {
      vote.moodId = $(this).attr('value');
      vote.moodPairId = $(this).attr('id');
      if(vote.moodId) {
        $.getJSON('/vote', {moodId: vote.moodId, moodPairId: vote.moodPairId},
                function(data){
                  $('#stats').html("Today<br/>");
                  $.each(data, function(name,votes){
                    $('#stats').append(votes+"% voted for "+name+"<br/>");
                  });
                  vote.loadPair();
                  // location.reload(); 
                });

      }

    });
  },

  loadStats: function() {
    $.get('/moodStats', {moodPairId: vote.moodPairId}, function(data) {
      $('#stats').html(data);
      var left = $('#stat1').attr('value');
      var right = $('#stat2').attr('value');


      leftpixel = ((left/100) * 600)|0;
      rightpixel = ((right/100) * 600)|0;
      
      $('#horizontal_stats_bar_left').css("width",leftpixel+"px");
      $('#horizontal_stats_bar_right').css("width",rightpixel+"px");
      

    });
  },

}