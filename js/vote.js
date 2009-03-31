$(document).ready(function() {
    vote.init();
});

var vote = {
  url: '/vote/',
  moodId:     null,
  moodPairId: null,
  
  init: function() {
    vote.listen();
  },

  listen: function() {
    $('.moodlink').click( function() {
      vote.moodId = $(this).attr('value');
      vote.moodPairId = $(this).attr('id');
      if(vote.moodId) {
          $.get('/vote', {moodId: vote.moodId}, function() { 
            vote.loadStats();
//            $('#moods').html("THanks");
            });
      }

    });
  },

  loadStats: function() {
    
  }
}