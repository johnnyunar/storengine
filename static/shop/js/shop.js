$(document).ready(function () {
    $('.product-card-square, .product-card-sm').on('click', function (event) {
        if (event.target.tagName !== 'BUTTON') {
            let id = $(this).data('id');
            $('#product-overlay').attr('style', 'display: flex');
            $('*[data-id=' + id + ']').fadeIn(300);
        }
    });

    $('.related-products img').on('click', function (event) {
        if (event.target.tagName !== 'BUTTON') {
            let id = $(this).data('id');
            $(this).closest('.product-modal').hide();
            $('*[data-id=' + id + ']').show();
        }
    });

    // $('#product-overlay').on('click', function (event) {
    //     console.log(event.target.tagName);
    //     if (event.target.tagName !== 'BUTTON' && event.target.tagName !== 'LABEL' && event.target.tagName !== 'INPUT') {
    //         $('.product-modal, #product-overlay').fadeOut(300);
    //     }
    // });

    $('.close').on('click', function () {
        $('.product-modal, .overlay').fadeOut(300);
    });
});