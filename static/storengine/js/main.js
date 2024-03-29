$(document).ready(function () {

    try {
        new Splide('.splide', {
            type: 'loop',
            perPage: 1,
            autoplay: true,
            interval: 5000,
        }).mount();
    } catch (e) {
    } // If there is no splide in page, do nothing

    $("#closeNotification").on("click", function () {
        $("#notification").slideUp();
    });

    $("#nav-link-cart, #cart-close-text, .cart-close").on("click", function () {
        $("#cart").toggle("slide", {direction: "right"}, 300);
    });

    $("#cart").on("click", "#cart-close", function () {
        $("#cart").toggle("slide", {direction: "right"}, 300);
    });

    $("#accept-important-cookies, #accept-all-cookies, #cookie-modal-content > .modal-close").on("click", function () {
        $(this).parent().parent().fadeOut("fast");
    });

    $("#cookie-modal").click(function () {
        $(this).fadeOut("fast");
    }).children().click(function (e) {
        e.stopPropagation();
    });

    $("#cookie-settings-button").on("click", function () {
        $("#cookie-modal").css("display", "flex");
    });

    let navbar = document.getElementsByClassName('navbar')[0];
    let mainNav = document.getElementById('js-menu');
    let navBarToggle = document.getElementById('js-navbar-toggle');

    navBarToggle.addEventListener('click', function () {
        mainNav.classList.toggle('active');
        navbar.classList.toggle('active-navbar');
        navBarToggle.firstElementChild.classList.toggle('fa-bars');
        navBarToggle.firstElementChild.classList.toggle('fa-times');
    });

    $(window).scroll(function () {
        var scrollTop = $(this).scrollTop();

        $('.main-navbar').css({
            background: function () {
                var elementHeight = $(this).height(),
                    opacity = ((1 - (elementHeight - scrollTop) / elementHeight) * 0.8);

                return `rgba(18, 18, 18, ${opacity})`;
            }
        });
    });

    inView('.count').on('enter', el => $(el).prop('Counter', 0).animate({
        Counter: $(el).text().replace(/[^0-9.]/g, '')
    }, {
        duration: 2000,
        easing: 'swing',
        step: function (now) {
            if ($(el).text().includes("+")) {
                $(el).text(Math.ceil(now).toString() + "+");
            } else {
                $(el).text(Math.ceil(now));
            }
        },
    }));

    $('.question').on('click', function () {
        $(this).next().slideToggle();
    });

    $('.watch-button').on('click', function () {
        $(this).parent().hide();
        $(this).parent().parent().find('.testimonial-video-embed').slideToggle();
    });

    $('.back-button').on('click', function () {
        $(this).parent().find('iframe')[0].contentWindow.postMessage('{"event":"command","func":"' + 'pauseVideo' + '","args":""}', '*');
        $(this).parent().hide();
        $(this).parent().parent().find('.testimonial-text').show();
    });

    $('.splide__arrow').on('click', function () {
        $('.testimonial-video-embed iframe').contentWindow.postMessage('{"event":"command","func":"' + 'pauseVideo' + '","args":""}', '*');
    });

    $('#shipping-address-heading').on('click', function () {
        $('#shipping-address-form').slideToggle();
        $(this).find('i').toggleClass('fa-caret-down fa-caret-right');
    });

    const packetaApiKey = 'dd307346f095f04b';

    const packetaOptions = {
        valueFormat: "\"Packeta\",id,carrierId,carrierPickupPointId,name,city,street"
    };

    function showSelectedPickupPoint(point) {
        // Add here an action on pickup point selection
        const saveElement = document.querySelector(".packeta-selector-value");
        saveElement.innerText = '';
        if (point) {
            $("#packeta-point-id").val(point.id);
            $("#packeta-point-name").show();
            $("#packeta-point-name").addClass("validated");
            $("#packeta-point-name").val(point.name);
        }
    }

    $('.packeta-selector-open, #packeta-point-name').on('click', function () {
        Packeta.Widget.pick(packetaApiKey, showSelectedPickupPoint, packetaOptions);
    });

});