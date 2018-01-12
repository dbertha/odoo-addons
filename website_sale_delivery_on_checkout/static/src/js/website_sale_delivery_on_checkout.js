odoo.define('website_sale.delivery_on_checkout', function (require) {
"use strict";

var base = require('web_editor.base');
var core = require('web.core');
var _t = core._t;
var ajax = require('web.ajax');


$(document).ready(function () {

    // When choosing an delivery carrier, update the quotation and the acquirers
    var $carrier = $("#delivery_carrier");
    $carrier.find("input[name='delivery_type']").click(function (ev) {
        var carrier_id = $(ev.currentTarget).val();

        ajax.jsonRpc("/shop/update_carrier_id", 'call', {'carrier_id': parseInt(carrier_id)})
            .then(function (data) {
                console.log(data);
                $(".shipping_id_div").toggleClass('hidden', data['is_pickup']);
                if(! data['is_pickup']){
                    $("select[name='shipping_id']").val(0).change();
                }
                else{
                    $("select[name='shipping_id']").prop("selectedIndex", 1).change();
                }
                _.each(Object.getOwnPropertyNames(data), function(field){
                    console.log(field);
                    if(field == 'shipping_country_id'){
                        $("select[name='shipping_country_id']").val(data[field]).change();
                    }
                    else{

                        console.log($("input[name='" + field + "']"));
                        // console.log($("input[data-oe-field='" + field + "']"));
                        console.log($("span[data-oe-field='" + field + "'] > span"));
                        $("input[name='" + field + "']").val(data[field]);
                        $("span[data-oe-field='" + field + "'] > span").text((isNaN(data[field]) || Number.isInteger(data[field]) || typeof(data[field]) === "boolean" || typeof(data[field]) === "string") && data[field] || typeof(data[field]) !== "boolean" && data[field].toFixed(2));
                    }
                });

                // _.each(product_dom, function (prod) {
                //     var current = $(prod).data("attribute_value_ids");
                //     for(var j=0; j < current.length; j++){
                //         current[j][2] = data[current[j][0]];
                //     }
                //     $(prod).trigger("change");
                // });
            });
        // window.location.href = '/shop/checkout?carrier_id=' + carrier_id;
    });

    $("input[name='delivery_mode']").click(function (ev) {
        var option = $(ev.currentTarget).val();
        console.log(option);
        $("label.store").toggleClass('hidden', ! (option === 'store'));
        $("label.delivery").toggleClass('hidden', ! (option === 'delivery'));
        
    });

    $(".oe_website_sale select[name='shipping_id']").on('change', function () {
        var value = $(this).val();
        var $provider_free = $("select[name='country_id']:not(.o_provider_restricted), select[name='state_id']:not(.o_provider_restricted)");
        var $provider_restricted = $("select[name='country_id'].o_provider_restricted, select[name='state_id'].o_provider_restricted");
        if (value == 0) {
            // Ship to the same address : only show shipping countries available for billing
            $provider_free.hide().attr('disabled', true);
            $provider_restricted.show().attr('disabled', false).change();
        } else {
            // Create a new address : show all countries available for billing
            $provider_free.show().attr('disabled', false).change();
            $provider_restricted.hide().attr('disabled', true);
        }
    });

});

});