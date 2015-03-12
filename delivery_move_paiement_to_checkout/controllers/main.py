# -*- coding: utf-8 -*-
import logging
import openerp
from openerp import http
from openerp.http import request
import openerp.addons.website_sale.controllers.main

_logger = logging.getLogger(__name__)
class website_sale(openerp.addons.website_sale.controllers.main.website_sale):

    @http.route(['/shop/checkout'], type='http', auth="public", website=True)
    def checkout(self, **post):
        cr, uid, context = request.cr, request.uid, request.context

        order = request.website.sale_get_order(force_create=1, context=context)
        #adapt when delivery method is changed
        carrier_id = post.get('carrier_id')
        _logger.debug("carrierID : " + carrier_id)
        _logger.error("Error : carrierID : " + carrier_id)
        if carrier_id:
            carrier_id = int(carrier_id)
            _logger.debug("carrierID : " + carrier_id)
            _logger.error("Error : carrierID : " + carrier_id)
            _logger.info("Info : carrierID : " + carrier_id)
        if order:
            request.registry['sale.order']._check_carrier_quotation(cr, uid, order, force_carrier_id=carrier_id, context=context)
            if carrier_id:
                return request.redirect("/shop/checkout")

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        values = self.checkout_values()
        #need delivery informations
        sale_order_obj = request.registry.get('sale.order')
        values.update(sale_order_obj._get_website_data(cr, uid, order, context))
        #

        return request.website.render("website_sale.checkout", values)