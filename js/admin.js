$(document).ready(function() {
    admin.init();
});

var admin = {
  url: '/add',
  data:     null,
  limit: 10,
  
  init: function() {
    admin.loadMoods();
    
    autoFill($("#mood1"), "Enter Mood");
    autoFill($("#mood2"), "Enter Mood");
    
    admin.listen();
  },

  listen: function() {
    $('#addMoodsForm').ajaxForm({
          beforeSubmit:  inputCheck,
          success: function() {
                                // if(accountDisabled) {
                                //     location.href = admin.url;
                                // }
//                                $('#listMoods').
                                $('#notify').html("Moods Added!");
                                $('#notify').fadeIn(800);
                                admin.loadMoods();
                                var timer = setTimeout("$('#notify').fadeOut(1000);clearTimeout(timer);", 3000);
                                }
    });
    
    $('.rmmood').click( function() {
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
  
  loadMoods: function() {
    $.get('/moodList', {limit: admin.limit}, function(data) {
      $('#moodDisplay').html(data);
    });
  },

}

function inputCheck(formData) 
{
  if((formData[0].name == "mood1") && (formData[0].name == "mood1"))
  {
    if((formData[0].value != "") || (formData[0].value != ""))
    {
      var message = "please enter two words that make up a Pair of opposite moods.";
      return true;
    }
  }
  $('#notify').html("<strong class=\"error\">please enter two words that make up a Pair of opposite moods.</strong>");
  $('#notify').fadeIn(800);
  var timer = setTimeout("$('#notify').fadeOut(1000);clearTimeout(timer);", 3000);

    return false;
}

function autoFill(id, v){
	$(id).css({ color: "#b2adad" }).attr({ value: v }).focus(function(){
		if($(this).val()==v){
			$(this).val("").css({ color: "#333" });
		}
	}).blur(function(){
		if($(this).val()==""){
			$(this).css({ color: "#b2adad" }).val(v);
		}
	});

}

