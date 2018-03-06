$(document).ready(function () {
    $("#selectErrorSite").change(function () {
    var site_name = $("#selectErrorSite")[0].value;
    $.ajax({
        type: 'POST',
        url: "/daily_ajax_search/",
        data: {
            'site': site_name,
        },
        success: function (site_info) {
            $("#tr_1")[0].value=site_info.split(',')[0];
            $("#tr_2")[0].value=site_info.split(',')[1];
        }});
    });
});
