function foo(response) {
    document.getElementById('output').innerHTML = response.user_information.username
};

function hideInput() {
        $("#api_key_box").css("display", "none");
}

$(document).ready(function() {
    $("#progress").removeClass('running');
        $("input").click(function() {
            hideInput();
            var tag = document.createElement("script");
            tag.src = 'https://www.wanikani.com/api/user/c9d088f9a75b0648b3904ebee3d8d5fa/user-information?callback=foo';
            document.getElementsByTagName("head")[0].appendChild(tag);
        });
});