$(document).ready(function () {

    // When choosing an delivery carrier, update the quotation and the acquirers
    var $carrier = $("#delivery_carrier");
    $carrier.find("input[name='delivery_method']").click(function (ev) {
        var carrier_id = $(ev.currentTarget).val();
        window.location.href = '/shop/checkout?carrier_id=' + carrier_id;
    });

});
