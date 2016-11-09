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

function validateWanikaniApiKey(key) {
    var validKey = new RegExp('[0-9a-zA-Z].{31}$');
    console.log(key)
    return validKey.test(key)
}

function callWanikaniApi2(key) {
    $.ajax({
        url: 'https://www.wanikani.com/api/user/' + key + '/user-information',
        type: 'GET',
        dataType: 'jsonp',
        beforeSend: function() {
            $("#progress").css("visibility", "visible");
            $("#progress").removeClass('running').delay(10).queue(function(next) {
                $(this).addClass('running');
                next();
            });
        },
        success: function(data) {
            console.log(data);
            $("body").append("p").text(data);
        },
    });
}

function makeWanikaniApiCall(key) {
    if(validateWanikaniApiKey(key)) {
        callWanikaniApi2();
    }
    else{
        console.log("error")
    }
}

$(document).ready(function() {
    $("#progress").removeClass('running');
        $("input").click(function() {
            makeWanikaniApiCall($("input:text").val())
            //validateWanikaniApiKey('c9d088f9a75b0648b3904ebee3d8d5fa')
            //hideInput();
            //callWanikaniApi2();
        });
});