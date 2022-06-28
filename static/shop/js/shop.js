$(document).ready(function () {
    $(".product-card-square, .product-card-sm").on("click", function (event) {
        if (event.target.tagName !== "BUTTON") {
            let id = $(this).data("id");
            $("#product-overlay").attr("style", "display: flex");
            $('*[data-id=' + id + ']').fadeIn(300);
        }
    });

    $("#product-overlay").on("click", function (event) {
        console.log(event.target.tagName);
        if (event.target.tagName !== "BUTTON") {
            $(".product-modal, #product-overlay").fadeOut(300);
        }
    });

    $(".close").on("click", function () {
        $(".product-modal, .overlay").fadeOut(300);
    });
});