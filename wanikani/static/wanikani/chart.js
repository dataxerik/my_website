$(document).ready(function() {
    $("nav.submenu a").click(function(){
        selectedId = $(this).attr('href').replace('#', '')
        $(".section").each(function(i){
            if (selectedId !== $(this).attr('class').split(' ')[0]) {
                $(this).addClass('hide');
            } else {
                $(this).removeClass('hide');
            }
        });
    });
    if ($(".hide")) {
        $(".section").each(function(i){
            if ($(this).attr('class').split(' ')[0] !== "jlpt") {
                $(this).addClass('hide');
            } else {
                $(this).removeClass('hide');
            }
        });
    }
});