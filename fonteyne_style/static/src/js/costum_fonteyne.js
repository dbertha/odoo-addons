
//temp hide
$('head').append("<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='//www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','GTM-NSDHJS');</script>");




//if (window.location.href.indexOf("shop") > -1) {
//    $("#right_column").hide();
//}

if (window.location.href.indexOf("shop/type/box-7") > -1) {
    $('#exclusiveOffer').modal({
        backdrop: 'static',
        keyboard: false
    })



    if (localStorage.getItem("ftkpromo") != "FTKsavoureuxEtSaine") {
        console.log("getItem = " + localStorage.getItem("ftkpromo"));
        $('#exclusiveOffer').modal('show');

    }
    if (localStorage.getItem("ftkpromo") == "FTKsavoureuxEtSaine") {
        $('#exclusiveOffer').modal('hide');


    }

    $(".promoSubmit").click(function () {
        var inputCode = $(".promoCode").val();
        if (inputCode == "FTKsavoureuxEtSaine") {

            localStorage.setItem("ftkpromo", "FTKsavoureuxEtSaine");
            $('#exclusiveOffer').modal('hide');
        } else {
            $(".promoError").removeClass("hidden");
        }

    });



}
var link;
$("header a").click(function (e) {
    console.log(this);
    if (window.location.href.indexOf("shop/type/the-horizon") > -1 && !$(this).hasClass("langToggle")) {
        console.log(this);
        e.preventDefault();
        link = $(this).attr("href");
        $('#warningExclusive').modal('show');
    }
    if (window.location.href.indexOf("shop/type/box-7") > -1 && !$(this).hasClass("langToggle")) {
        e.preventDefault();
        link = $(this).attr("href");
        $('#warningExclusiveEntreprise').modal('show');
    }
});
$('.warningExclusiveOk').click(function () {
    goToLink();
});
function goToLink() {
    if (window.location.href.indexOf("nl_BE") > -1) {
        link = "/nl_BE" + link;
    }
    window.location.href = link;
}
// .promoCode input promoSubmit submit


// the horizon logic

if (window.location.href.indexOf("the-horizon-8") > -1) {
    $('#theHorizon').modal({
        backdrop: 'static',
        keyboard: false
    })



    if (localStorage.getItem("ftkpromo2") != "TheHorizonTheHorizon") {
        console.log("getItem = " + localStorage.getItem("ftkpromo2"));
        $('#theHorizon').modal('show');
    }
    if (localStorage.getItem("ftkpromo2") == "TheHorizonTheHorizon") {
        $('#theHorizon').modal('hide');


    }


    $(".promoSubmit2").click(function () {
        var inputCode = $(".promoCode2").val();
        if (inputCode == "TheHorizonTheHorizon") {

            localStorage.setItem("ftkpromo2", "TheHorizonTheHorizon");
            $('#theHorizon').modal('hide');
        } else {
            $(".promoError2").removeClass("hidden");
        }

    });

    if (window.location.href.indexOf("nl_BE") > -1) {

        $(".horizonNL").removeClass("hidden");
    } else {
        $(".horizonFR").removeClass("hidden");


    }




}


// odoo bug?
// email anti theft script bug?
// 
if (window.location.href.indexOf("contact-jo") > -1 && window.location.href.indexOf("nl_BE") > -1) {
    $(".tempFix").html("We hechten meer belang aan uw persoonlijkheid dan aan uw ervaring. Bent u: <strong>dynamisch, georganiseerd, enthousiast</strong> en wenst u deel uit te maken van een onderneming in volle groei? Stuur dan uw <strong>CV en motivatiebrief</strong> naar jobs@fonteynethekitchen.be")
}
if (window.location.href.indexOf("type/ffy-2") > -1) {
    $("ul.mt16>li:contains('Fit'):first").addClass("hidden");
}

// change delivery condition title for take away

if (window.location.href.indexOf("checkout") > -1) {
    if (!($(".livraison_wrap span:contains('LIVRAISON')").length != 0)) {
        $(".livraison_wrap h3").html("Enl&#232;vement en magasin:");
    }

}



// the custom added snippet was not translateable in the front end editor
if (window.location.href.indexOf("contact-us") > -1) {
    if (window.location.href.indexOf("nl_BE") > -1) {
        $(".contact_us_form select.form-control option").each(
                function () {
                    if ($(this).text() == "Sujet") {
                        $(this).text("onderwerp");
                    }
                    if ($(this).text() == "MAGASIN") {
                        $(this).text("winkels");
                    }
                    if ($(this).text() == "DIETETIQUE") {
                        $(this).text("dieten");
                    }
                    if ($(this).text() == "EVENEMENT") {
                        $(this).text("evenementen");
                    }
                    if ($(this).text() == "PRODUITS") {
                        $(this).text("producten");
                    }
                    if ($(this).text() == "CARTES") {
                        $(this).text("kaarten");
                    }
                    if ($(this).text() == "SALLE DE WOLUWE") {
                        $(this).text("zaal in Woluwe");
                    }


                });

        $("input[name='contact_name']").attr("placeholder", "Naam");
        $("input[name='phone']").attr("placeholder", "Telefoonnummer");
        $("textarea[name='description']").attr("placeholder", "BERICHT");

    } else {
        $("input[name='contact_name']").attr("placeholder", "Nom");
        $("input[name='phone']").attr("placeholder", "numero de telephone");
        $("textarea[name='description']").attr("placeholder", "message");
    }

    ;
}

// translate login page
if (window.location.href.indexOf("web/login") > -1) {
    if (window.location.href.indexOf("nl_BE") > 1) {
        //eventuele nl vertaling
    } else {
        $("label[for='login']").text("Email");
        // $("button[type='submit']").text("Connection");

    }
    $("main").append("<img class='img-responsive imgLogin' src='/website/image/ir.attachment/1878_8b5a049/datas'/>");

}
// Societe et TVA cacher

if ((window.location.href.indexOf("confirm_order") > -1) || (window.location.href.indexOf("checkout") > -1)) {

    var addAfter = $("label:contains('nom')").parent();
    var societe = $("label:contains('Soci')").parent();
    var tva = $("label:contains('TVA')").parent();
    addAfter.append("<div class='onderneming'><input type='checkbox' class='checkMe' name='showSociete'/> <div class='ondernemingText'><strong>Soci&#233;t&#233;</strong></div></div>");
    societe.hide();
    tva.hide();

    $('.checkMe').click(function () {
        if ($(this).is(':checked')) {
            societe.show();
            tva.show();
        } else {
            societe.hide();
            tva.hide();
        }
    });



}



//contact jobs translation, snippets cannot be translated
if (window.location.href.indexOf("nl_BE") > -1 && window.location.href.indexOf("contact-job") > -1) {
    $(".well").text("Schrijf een mail naar jobs@fonteyneATHOME.be vergezeld van een CV en een motivatiebrief");
}
;
// adding extra mon panier button in webshop
// 

if (window.location.href.indexOf("/shop/") > -1) {
    if (window.location.href.indexOf("nl_BE") > -1) {

        $(".products-cat.mt16").append("<a href='/shop/cart'><div class='monPanierButton'>mijn winkelwagen</div></a>");
    } else {

        $(".products-cat.mt16").append("<a href='/shop/cart'><div class='monPanierButton'>mon panier</div></a>");
    }
}
//
//
//
//
//adding introduction tekst/breadcrumbs for nos cartes
if (window.location.href.indexOf("/shop/") > -1) {
    if (window.location.href.indexOf("nl_BE") > -1) {

        $(".shop-nos-cartes-breadcrumb h3").text("ONZE KAARTEN >");
    } else {

        $(".shop-nos-cartes-breadcrumb h3").text("NOS CARTES >");
    }
}

//
// seizoenskaart
//
if (window.location.href.indexOf("type/normal-1") > -1) {
    if (window.location.href.indexOf("nl_BE") > -1) {
        //Special K request:
        $("#saisonNL").removeClass("hidden");
        if (window.location.href.indexOf("wijnen") > -1) {
            $("#saisonNL").addClass("hidden");
        }

    } else {
        $("#saisonFR").removeClass("hidden");

        if (window.location.href.indexOf("vins") > -1) {
            $("#saisonFR").addClass("hidden");

        }
    }
}
//
// ffy
//
if (window.location.href.indexOf("type/ffy-2") > -1) {
    if (window.location.href.indexOf("nl_BE") > -1) {
        $("#ffyNL").removeClass("hidden");
        if (window.location.href.indexOf("box-for-all") > -1) {

            $(".boxForAll").removeClass("hidden");
        }
        if (window.location.href.indexOf("box-fit-for") > -1) {

            $(".boxFfy").removeClass("hidden");
        }
        if (window.location.href.indexOf("veggie") > -1) {

            $(".boxVeggie").removeClass("hidden");
        }
        if (window.location.href.indexOf("plaisir") > -1) {

            $(".plaisirDe").removeClass("hidden");
        }
        if (window.location.href.indexOf("a-la-carte-hoofdgerechten") > -1) {

            $(".alcPlats").removeClass("hidden");
        }
        if (window.location.href.indexOf("a-la-carte-voorgerechten") > -1) {

            $(".alcEntrees").removeClass("hidden");
        }


    } else {

        $("#ffyFR").removeClass("hidden");
        if (window.location.href.indexOf("box-for-all") > -1) {

            $(".boxForAll").removeClass("hidden");
        }
        if (window.location.href.indexOf("box-fit-for") > -1) {

            $(".boxFfy").removeClass("hidden");
        }
        if (window.location.href.indexOf("veggie") > -1) {

            $(".boxVeggie").removeClass("hidden");
        }
        if (window.location.href.indexOf("plaisir") > -1) {

            $(".plaisirDe").removeClass("hidden");
        }
        if (window.location.href.indexOf("a-la-carte-plats") > -1) {

            $(".alcPlats").removeClass("hidden");
        }
        if (window.location.href.indexOf("a-la-carte-entrees") > -1) {

            $(".alcEntrees").removeClass("hidden");
        }

    }
}
//
// Catering webshop
//
if (window.location.href.indexOf("type/events-3") > -1) {
    if (window.location.href.indexOf("nl_BE") > -1) {
        $("#cateringNL").removeClass("hidden");
    } else {

        $("#cateringFR").removeClass("hidden");
    }
}
//
// Exclusive webshop
//
if (window.location.href.indexOf("type/box-7") > -1) {
    if (window.location.href.indexOf("nl_BE") > -1) {
        $(".boxExclusiefNL").removeClass("hidden");
    } else {

        $(".boxExclusiefFR").removeClass("hidden");
    }
}
// adding extra menu at bottom of page in webshop

if (window.location.href.indexOf("/shop/") > -1) {
    $(".products").after("<div class='container bottom-nav products-listBottom'></div>"); // create wrapper for new menu
    $("#shop_selection").clone().appendTo($(".bottom-nav")); // duplicate existing menu and add

}

// adding more buttons in mon panier
if (window.location.href.indexOf("cart") > -1) {
    if ($(".well").length || ($("tbody.suggested_products_wrap").length)) {
        console.log($("tbody.suggested_products_wrap").length);
        console.log(!$(".well").length);
        console.log("there should be true or false here...");
        // true indien er geen warning staat (leeg) OF als die tabel leeg, 0 is = false
        $("#right_column").after("<div class='container continueMoreShopping'></div>");
        $("#cart_total").clone().appendTo($(".continueMoreShopping"));
        $("#cart_total").after("<div class='clearBoth'></div>");
        $(".btn-shop_online.mb32").clone().appendTo($(".continueMoreShopping"));
    }
}
//

//contact section show store info on store click
$(".winkels_target li").click(function () {
    $(".introFoto").fadeOut();
    $(".introText").fadeOut();


    $(".winkelsOverzicht").removeClass("hidden");

});

//show landing text

if (window.location.href.indexOf("contact-shop") > -1) {
    if (window.location.href.indexOf("nl_BE") > -1) {
        $(".kiesNL").removeClass("hidden");
    } else {

        $(".kiesFR").removeClass("hidden");
    }
}




// make tous les categorie not browseable
//take away webshop
if (window.location == "http://www.fonteynethekitchen.be/shop/type/normal-1" || window.location == "http://fonteynethekitchen.be/shop/type/normal-1") {
    window.location.href = "http://www.fonteynethekitchen.be/shop/type/normal-1/category/plats-volaille-26";

}

if (window.location == "http://www.fonteynethekitchen.be/nl_BE/shop/type/normal-1" || window.location == "http://fonteynethekitchen.be/nl_BE/shop/type/normal-1") {
    window.location.href = "http://www.fonteynethekitchen.be/nl_BE/shop/type/normal-1/category/hoofdgerechten-gevogelte-26";

}

//FFY webshop    
if (window.location == "http://www.fonteynethekitchen.be/shop/type/ffy-2" || window.location == "http://fonteynethekitchen.be/shop/type/ffy-2") {
    window.location.href = "http://www.fonteynethekitchen.be/shop/type/ffy-2/category/entrees-41";

}
if (window.location == "http://www.fonteynethekitchen.be/nl_BE/shop/type/ffy-2" || window.location == "http://fonteynethekitchen.be/nl_BE/shop/type/ffy-2") {
    window.location.href = "http://www.fonteynethekitchen.be/nl_BE/shop/type/ffy-2/category/voorgerechten-41";

}

//catering webshop
if (window.location == "http://www.fonteynethekitchen.be/shop/type/events-3" || window.location == "http://fonteynethekitchen.be/shop/type/events-3") {
    window.location.href = "http://www.fonteynethekitchen.be/shop/type/events-3/category/aperitif-106";

}
if (window.location == "http://www.fonteynethekitchen.be/nl_BE/shop/type/events-3" || window.location == "http://www.fonteynethekitchen.be/nl_BE/shop/type/events-3") {
    window.location.href = "http://www.fonteynethekitchen.be/nl_BE/shop/type/events-3/category/aperitif-106";

}

if (window.location.href.indexOf("/shop/category/") > 1) {
    if (window.location.href.indexOf("BE") > 1) {

        window.location.href = "http://www.fonteynethekitchen.be/nl_BE/page/nos-cartes";
    } else {
        window.location.href = "http://www.fonteynethekitchen.be/page/nos-cartes";
    }
}



//
//
//
if (window.location.href.indexOf("nos-menu") > -1 || window.location.href.indexOf("nos-cartes")) {


    $('.pdf').click(function () {

        var link = $(this).attr("data-link");
        if (link != "") {
            window.open(link, '_blank');
        }
    });
    $('.shop').click(function () {
        var link = $(this).attr("data-link");
        if (window.location.href.indexOf("nl_BE") > -1) {
            link = "/nl_BE" + link;
        }
        window.location.href = link;
    });

}
;
// NAV 
//navbar hide or show on scroll
/* 
 */

$(".navbar-fonteyne").addClass("navbar-fonteyne_scroll");


if ($("#wrap").hasClass("transparent_nav")) {

    $(".navbar-fonteyne").removeClass("navbar-fonteyne_scroll");

}

$(window).scroll(function () {


    if ($("#wrap").hasClass("transparent_nav")) {
        var scrolltop = $(window).scrollTop();
        if (scrolltop > 100) {

            $(".navbar-fonteyne").addClass("navbar-fonteyne_scroll");

        } else {

            $(".navbar-fonteyne").removeClass("navbar-fonteyne_scroll");
            // HIDE BG CHECKER EFFECT
            if ($(document).width() < 1226) {
                $(".navbar-fonteyne").addClass("navbar-fonteyne_scroll");
            }
        }
    }


});


$(document).ready(function () {
    $('a[href^="#"]').on('click', function (e) {
        e.preventDefault();

        var target = this.hash;
        var $target = $(target);

        $('html, body').stop().animate({
            'scrollTop': $target.offset().top
        }, 900, 'swing', function () {
            window.location.hash = target;
        });
    });
});
// FAQ HIDE


$('.contact_faq-question').toggle(function () {
    $(this).addClass("contact_faq-question-active");
    $(this).next().slideDown(300);
}, function () {
    $(this).removeClass("contact_faq-question-active");
    $(this).next().slideUp(300);
});



// SECONDARY NAV


$(".target").css('display', 'none');
$(".target_first").css('display', 'block');


$(".nav_secondary ul li").each(function () {

    var content_li = $(this).text().replace(/[^a-z0-9 -]/g, '') // remove invalid chars
            .replace(/\s+/g, '-') // collapse whitespace and replace by -
            .replace(/-+/g, '-'); // collapse dashes;
    $(this).addClass(content_li);



    $(this).click(function () {
        var content_li = $(this).text().replace(/[^a-z0-9 -]/g, '') // remove invalid chars
                .replace(/\s+/g, '-') // collapse whitespace and replace by -
                .replace(/-+/g, '-'); // collapse dashes ;
        $("." + content_li + "_target").delay(400).fadeIn(400);

        $(".target").not("." + content_li + "_target").fadeOut(400);
        $(".nav_secondary ul li").removeClass('active_secnav');
        $(this).addClass('active_secnav');


    });


});



// THIRD NAV


$(".target_third").css('display', 'none');
$(".target_third_first").css('display', 'block');

if (!(window.location.href.indexOf("contact-shop") > -1)) {

    $(".nav_third ul li:first-child").addClass('active_thirdnav');
}


$(".nav_third ul li").each(function () {

    var content_li = $(this).text().replace(/[^a-z0-9 -]/g, '') // remove invalid chars
            .replace(/\s+/g, '-') // collapse whitespace and replace by -
            .replace(/-+/g, '-'); // collapse dashes;
    $(this).addClass(content_li);



    $(this).click(function () {
        var content_li = $(this).text().replace(/[^a-z0-9 -]/g, '') // remove invalid chars
                .replace(/\s+/g, '-') // collapse whitespace and replace by -
                .replace(/-+/g, '-'); // collapse dashes ;
        $("." + content_li + "_target_third").delay(400).fadeIn(400);
        $(".target_third").not("." + content_li + "_target_third").fadeOut(400);
        $(".nav_third ul li").removeClass('active_thirdnav');
        $(this).addClass('active_thirdnav');


    });


});


// SLIDE SHOW



$('.slider-arrow--left').click(function () {
    prevSlide($(this).parents('.slider').find('.slider-strip'));
});
//clicking image goes to next slide
$('.slider-arrow--right').click(function () {
    nextSlide($(this).parents('.slider').find('.slider-strip'));
});

//initialize show
iniShow();

function iniShow() {
    //show first image
    $('.slider-strip').each(function () {
        $(this).find('img:first').fadeIn(900);
    })
}

function prevSlide($slides) {
    $slides.find('img:last').prependTo($slides);
    showSlide($slides);
}

function nextSlide($slides) {
    $slides.find('img:first').appendTo($slides);
    showSlide($slides);
}

function showSlide($slides) {
    //hide (reset) all slides
    $slides.find('img').hide();
    //fade in next slide
    $slides.find('img:first').fadeIn(900);
}



// SHOP ONLINE 

if (window.location.href.indexOf("nos-cartes") > -1) {
    if (window.location.href.indexOf("nl_BE") > -1) {

        $(".carteFR").addClass("hidden");
        $(".carteNL").removeClass("hidden");
    } else {

        $(".carteNL").addClass("hidden");
        $(".carteFR").removeClass("hidden");
    }


}


// SHOP ONLINE OFFERS


var current_url = window.location.href;

var shop = "shop";

var shop_week = "ffy-2";
var shop_week_title = "Shop online - Fit for you";

var shop_christmas = "christmas-4";
var shop_christmas_title = "Shop online - Christmas time";

var shop_today = "normal-1";
var shop_today_title = "Shop online - Today";

var shop_events = "events-3";
var shop_events_title = "Shop online - Today";

var product = "product";





if (current_url.indexOf(shop) > -1) {

    $(".navbar-fonteyne").addClass("navbar-fonteyne_scroll");
    $('.nav_secondary').css('margin-top', '80px');
    $('.header_main').hide();
    $(window).scroll(function () {

        var scrolltop = $(window).scrollTop();
        if (scrolltop > 100) {

            $(".navbar-fonteyne").addClass("navbar-fonteyne_scroll");

        } else {

            $(".navbar-fonteyne").addClass("navbar-fonteyne_scroll");
            // HIDE BG CHECKER EFFECT
            if ($(document).width() < 1226) {
                $(".navbar-fonteyne").addClass("navbar-fonteyne_scroll");
            }
        }
    });

}



if (current_url.indexOf(shop_week) > -1) {

    $('.nav_secondary').css('margin-top', '80px');
    $(".oncept_week_target").fadeIn();

}

if (current_url.indexOf(shop_today) > -1) {

    $('.nav_secondary').css('margin-top', '80px');
    $(".oncept_today_target").fadeIn();
    $(".hop-online i").fadeOut();

}

if (current_url.indexOf(shop_events) > -1) {

    $('.nav_secondary').css('margin-top', '80px');
    $(".oncept_events_target").fadeIn();
    $(".hop-online i").fadeOut();

}





if (current_url.indexOf(product) > -1) {

    $(".navbar-fonteyne").addClass("navbar-fonteyne_scroll");
    $('.product_single_main').css('margin-top', '80px');

}


// H1 HEADER APPEAR


$('.header_main h1').delay(500).queue('fx', function () {
    $(this).addClass('title_h1_appear');
});

$('.header_main h3').delay(1000).queue('fx', function () {
    $(this).addClass('title_h3_appear');
});

$('.navbar-fonteyne .navbar-nav').delay(200).queue('fx', function () {
    $(this).addClass('nav_appear');
});

$('.logo_nav').delay(200).queue('fx', function () {
    $(this).addClass('logo_nav_appear');
});


// HIDE DESCRIPTION PRODUCT

$('.description_button').toggle(function () {
    $(this).addClass("description_product_txt-active");
    $(this).next().slideDown(300);
}, function () {
    $(this).removeClass("description_product_txt-active");
    $(this).next().slideUp(300);
});



// FORM SELECT DISABLE ISSUE XML


$(".form-subject_jobs")
        .change(function () {



            var str = "";
            $(".form-subject_jobs option:selected").each(function () {
                str += $(this).val() + " ";
            });


            $(".job-post h3").text(str);
            $(".job_link").attr("href", "mailto:jobs@fonteynethekitchen.be?subject= EMPLOI " + str);
            $(".text-error").text('');


            if ($('.form-subject_jobs').children('option:first-child').is(':selected')) {

                $(".job_link").attr("href", "#");
                $(".text-error").text(str);
                $(".job-post h3").text('  ');

            }

        })

        .trigger("change");

$('.job_link').click(function () {


    if ($('.form-subject_jobs').children('option:first-child').is(':selected')) {

        $('.job_link').unbind('click');

    }

});



// OVERLAY VIDEO


$('.header_index_overlay_offers-open').click(function () {
    $(".header_index_overlay_offers").hide().fadeIn(300);
    $(".header_index_overlay_offers").addClass('header_index_overlay_offers-active');
});

$('.header_index_overlay_offers').click(function () {
    $(".header_index_overlay_offers").removeClass('header_index_overlay_offers-active');
    $(this).fadeOut(300);
});




$('.header_index_overlay_video-close').click(function () {

    $(".header_index_overlay_video").fadeOut(300);
    $(".header_index_overlay_video").removeClass('header_index_overlay_iframe-active');


});

$('.header_index_overlay_video-open').click(function () {

    $(".header_index_overlay_video").hide().fadeIn(300);
    $(".header_index_overlay_video").addClass('header_index_overlay_iframe-active');

});



$('.header_index_overlay_video').click(function () {
    $(this).fadeOut(300);
    $(".header_index_overlay_video").removeClass('header_index_overlay_iframe-active');
});



// OVERLAY 


$('.btnfs-carte').click(function () {

    $('.overlay-wrap').fadeIn(300);

});

$('.btnfs-liv').click(function () {

    $('.overlay-wrap').fadeIn(300);

});

$('.overlay-wrap .close').click(function () {

    $('.overlay-wrap').fadeOut(300);

});


$(document).on('keyup', function (evt) {
    if (evt.keyCode == 27) {
        $('.overlay-wrap').fadeOut(300);
    }
});




// Nav Webshop adjustments



if (current_url.indexOf(shop) > -1) {
    $("#products_grid_before li ul li.active").parent().parent().addClass("active");


}

// Email verification/ conformation alert!

if (current_url.indexOf("checkout")) {
    if (window.location.href.indexOf("nl_BE") > -1) {
        $("input[name='email']").after("<p>Indien u geen bevestigingsmailtje ontvangen hebt gelieve dan contact op te nemen met ons om de bestelling te bevestigen</p>");
    } else {
        //french

        $("input[name='email']").after("<p> ATTENTION: votre commande est valid" + decodeURI("&#233;") + "e uniquement si vous recevez un mail de confirmation. A d" + decodeURI("&#233;") + "faut contactez le 02 333 50 14</p>");




    }
}





/* Video controls and styling */

/*
 JS Modified from a tutorial found here: 
 http://www.inwebson.com/html5/custom-html5-video-controls-with-jquery/
 
 I really wanted to learn how to skin html5 video.
 */
;