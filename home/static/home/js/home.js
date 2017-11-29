$(".Works .card").hover(function() {
    elementID = "#" + $(this).attr("id") + "Desc";
    console.log(elementID);
    $(elementID).removeClass("hideDesc");
    }, function() {
    elementID = "#" + $(this).attr("id") + "Desc";
    $(elementID).addClass("hideDesc");
});

function hideDescriptions(elementID) {
    descriptionSelector = elementID;
    console.log("trying to select element with " + descriptionSelector);
    $(descriptionSelector).each(function() {
        console.log($(this));
        $(this).addClass("hideDesc");
    });
}

hideDescriptions(".Desc")