$(document).ready(function () {
$('.oe_website_sale').each(function () {
    var oe_website_sale = this;

    $(oe_website_sale).on("change", ".oe_cart input.js_quantity", function () {
        var $input = $(this);
        var value = parseInt($input.val(), 10);
        var $line = $(this).closest("tr"); //get line
        var price = parseFloat($line.find('td[name="price"]').find(".oe_currency_value").text().replace(',', '.')); 
        var $total = $line.find('td[name="total_line"]').find("span[id='custom_line_total']");
        var total_value = value * price;
        $total.html(total_value.toFixed(2).replace('.', ',') + ' €');
    });
});
}); 
