function resetPage() {

}

var apiHandler = {
    interval: 10000,

    progressHandler: '',

    init: function() {
        setTimeout(
            $.proxy(this.getApiData, this),

            this.intervalHandler
            );
    },

    startProgressBar: function() {
        $("#progress").css("visibility", "visible");
        function cycleProgressBar() {
            $("#progress").removeClass('running').delay(10).queue(function(next) {
                $(this).addClass('running');
                next();
             });
            return false;
        }
        cycleProgressBar();
        //progressHandler = setInterval(function() {cycleProgressBar();}, 4000);

    },

    getApiData: function () {
        var self = this;
        this.startProgressBar();
        self.init();

    },
}
function hideInput() {
        $("#api_key_box").css("display", "none");
    }


$(document).ready(function() {
    $("#progress").removeClass('running');
        $("input").click(function() {
            hideInput();
            apiHandler.init();
        });
});

/*
$(document).ready(function() {
    alert("Hi");
});*/