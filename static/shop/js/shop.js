$(document).ready(function () {
    $(".product-card-square").on("click", function () {
        let id = $(this).data("id");
        $("#product-overlay").attr("style", "display: flex");
        $('*[data-id=' + id + ']').fadeIn(300);
    }).find('.card-cta').click(function (e) {
        e.stopPropagation();
    });

    $("#product-overlay").on("click", function () {
        $(".product-modal, #product-overlay").fadeOut(300);
    }).children().click(function (e) {
        e.stopPropagation();
    });

    $(".close").on("click", function () {
        $(".product-modal, .overlay").fadeOut(300);
    });
});