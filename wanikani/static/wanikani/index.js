

function validateWanikaniApiKey() {
    var apiKey = $("#api_key_input")[0].value;
    console.log(apiKey);
    var validKey = new RegExp('[0-9a-zA-Z].{31}$');
    console.log(validKey.test(apiKey));
    return validKey.test(apiKey);
}

 // This is just dummy code from previous thoughts that I want to say just as a reference.
/*

function foo(response) {
    document.getElementById('output').text = response.user_information.username
};

function hideInput() {
        $("#api_key_box").css("display", "none");
}

function clearInput() {
        $("#api_key_box p").remove()
}

function writeError() {
        $("#api_key_box").append("<p></p>")
        $("#api_key_box p").addClass("error").text("invalid API key");
}

function redirectToDataPage(data_){
    window.open()
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
    tag.src = 'https://www.wanikani.com/api/v1.4/user/' + key + '/user-information?callback=foo';

    document.getElementsByTagName("head")[0].appendChild(tag);

}

function callWanikaniApi2(key) {
    $.ajax({
        url: 'https://www.wanikani.com/api/v1.4/user/' + key + '/user-information',
        type: 'GET',
        dataType: 'jsonp',
        beforeSend: function(settings) {
            $("#progress").css("visibility", "visible");
            $("#progress").removeClass('running').delay(10).queue(function(next) {
                $(this).addClass('running');
                next();
            });
        },
        success: function(data) {
            console.log(data);
            $("#api_key_box").append("p").text(data);
        },
    });
}

function makeWanikaniApiCall(key) {
    clearInput();
    if(validateWanikaniApiKey(key)) {
        callWanikaniApi2(key);
    }
    else{
        console.log("error")
        writeError();
    }
 }

$(document).ready(function() {
    $("#progress").removeClass('running');
        $("input").click(function() {
            makeWanikaniApiCall($("input:text").val().trim())
            //validateWanikaniApiKey('c9d088f9a75b0648b3904ebee3d8d5fa')
            //hideInput();
            //callWanikaniApi2();
        });
});*/