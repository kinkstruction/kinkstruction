$(document).ready(function(){

    $('[data-toggle="tooltip"]').each(function(){
        var $this = $(this);
        var placement = $this.data("placement");

        $this.tooltip({placement: placement});
    });

    $(".well").css("word-wrap", "break-word");
    $(".panel-body").css("word-wrap", "break-word");

    $(".moment-js").each(function(i, ts){
        var $this = $(this);
        $this.html(moment.utc($this.html()).fromNow());
    });

});
