jQuery(window).on('load', function () {
    $('.question').on('click', function () {
        $(this).next().slideToggle();
    });
});

