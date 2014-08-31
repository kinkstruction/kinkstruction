$(document).ready(function(){

    $('[data-toggle="tooltip"]').tooltip({'placement': 'bottom'});

    $(".well").css("word-wrap", "break-word");
    $(".panel-body").css("word-wrap", "break-word");

    $(".moment-js").each(function(i, ts){
        var $this = $(this);
        $this.html(moment.utc($this.html()).fromNow());
    });

});
