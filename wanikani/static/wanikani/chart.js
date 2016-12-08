$(document).ready(function() {
    $("nav#submenu a").click(function(){
        selectedId = $(this).attr('href')
        $("nav#submenu a").each(function(i){
            //console.log($(this).attr('href'))
            if (selectedId !== $(this).attr('href')) {
                $($(this).attr('href')).attr('class', 'hide');
            } else {
                $($(this).attr('href')).removeAttr('class', 'hide');
            }
        });
    });
    if ($(".hide")) {
        $("nav#submenu a").each(function(i){
            //console.log($(this).attr('href'))
            if ($(this).attr('href') !== "#jlpt") {
                $($(this).attr('href')).attr('class', 'hide');
            } else {
                $($(this).attr('href')).removeAttr('class', 'hide');
            }
        });
    }
});