$(document).ready(function(){

    $(".moment-js").each(function(i, ts){
        var $this = $(this);
        $this.html(moment.utc($this.html()).fromNow());
    });

});
