function foo(response) {
    document.getElementById('output').innerHTML = response.user_information.username
};

function hideInput() {
        $("#api_key_box").css("display", "none");
}

function callWanikaniApi() {
    var dfd = $.Deferred();

    function startProgressBar() {
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
    }
    startProgressBar();
    var tag = document.createElement("script");
    tag.src = 'https://www.wanikani.com/api/user/c9d088f9a75b0648b3904ebee3d8d5fa/user-information?callback=foo';

    document.getElementsByTagName("head")[0].appendChild(tag);

}

function callWanikaniApi2() {
    $.ajax({
        url: 'https://www.wanikani.com/api/user/c9d088f9a75b0648b3904ebee3d8d5fa/user-information',
        type: 'GET',
        dataType: 'jsonp',
        beforeSend: function() {
            console.log("HIIII")
            $("#progress").removeClass('running').delay(10).queue(function(next) {
                $(this).addClass('running');
                next();
            });
        },
        success: function(data) {
            console.log(data);
            $(document).get("head").append(data);
        },
    });
}

$(document).ready(function() {
    $("#progress").removeClass('running');
        $("input").click(function() {
            hideInput();
            callWanikaniApi2();
        });
});