odoo.define('website_sale_promo.website_sale_promo', function (require) {
    "use strict";

    var base = require('web_editor.base');
    var ajax = require('web.ajax');

    $('.oe_website_sale').each(function () {
        var oe_website_sale = this;
        
        $(oe_website_sale).on("change", ".oe_cart input.code_promo", function (event) {
            ajax.jsonRpc('/shop/cart/update_code_promo', 'call', {
                'code_promo': $("input[name='code_promo']").val()
            });
        });
    });
});