function resetPage() {

}

var apiHandler = {
    interval: 5000,


    progressHandler: '',

    init: function() {
        this.getApiData()
        //this.startProgressBar()
        /*setTimeout(
            $.proxy(this.getApiData, this),

            this.intervalHandler
            );*/
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
        progressHandler = setInterval(function() {cycleProgressBar();}, 4000);

    },

    getApiData: function () {
        var url = 'https://www.wanikani.com/api/user/c9d088f9a75b0648b3904ebee3d8d5fa/user-information';
        $.ajax( {url: 'https://www.wanikani.com/api/user/c9d088f9a75b0648b3904ebee3d8d5fa/user-information',
                datatyp: 'jsonp',
                success: function(data) {
                console.log('yay')
                }});

                /*
        .done(function(data) {
            console.log("HIIIIIIIIII");
            var data_ = data
        })
        .fail(function() {
            console.log("error")
        });
        console.log("HIIIIIIIIIII")*/
    /*
        var self = this;
        self.startProgressBar();
        self.init();
    */
    },
}

function getApiData() {
        var url = 'https://www.wanikani.com/api/user/c9d088f9a75b0648b3904ebee3d8d5fa/user-information';
        $.ajax( {url: 'https://www.wanikani.com/api/user/c9d088f9a75b0648b3904ebee3d8d5fa/user-information',
                datatyp: 'jsonp',
                success: function(data) {
                console.log('yay')
}})};

function hideInput() {
        $("#api_key_box").css("display", "none");
    }

function api(response) {
    var foo = response.requested_information;
    document.getElementById("output").innerHTML = foo.requested_information;
    console.log(foo);
};

$(document).ready(function() {
    $("#progress").removeClass('running');
        $("input").click(function() {
            hideInput();
            getApiData();
           /* var tag = document.createElement('script');
            tag.src = 'https://www.wanikani.com/api/user/c9d088f9a75b0648b3904ebee3d8d5fa/user-information?callback=api';
            document.getElementsByTagName("head")[0].appendChild(tag);*/
            //apiHandler.init();
        });
});

/*
$(document).ready(function() {
    alert("Hi");
});*/