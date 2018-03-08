$(document).ready(function () {
    $('html,body').animate({
        scrollTop: $("[id$='_this_']").offset().top - $(window).height()/2
    }, 1500);
});
