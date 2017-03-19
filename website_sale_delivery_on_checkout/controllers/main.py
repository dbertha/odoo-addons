# -*- coding: utf-8 -*-
import openerp
from openerp import http
from openerp import SUPERUSER_ID
from openerp.http import request
import openerp.addons.website_sale.controllers.main
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone
import pytz
import logging

_logger = logging.getLogger(__name__)
class website_sale(openerp.addons.website_sale.controllers.main.website_sale):

    @http.route(['/shop/checkout'], type='http', auth="public", website=True)
    def checkout(self, **post):
        _logger.debug("overloaded checkout")
        cr, uid, context = request.cr, request.uid, request.context
        order = request.website.sale_get_order(context=context)
        carrier_id = post.get('carrier_id')
        if carrier_id:
            carrier_id = int(carrier_id)
        if order:
            request.registry['sale.order']._check_carrier_quotation(cr, uid, order, force_carrier_id=carrier_id, context=context)
            if carrier_id:
                #refresh page with new delivery method
                return request.redirect("/shop/checkout")

        res = super(website_sale, self).checkout(**post)
        return res

    def checkout_values(self, data=None):
        """Overload to add delivery data"""
        values = super(website_sale, self).checkout_values(data)
        sale_order_obj = request.registry.get('sale.order')
        order = request.website.sale_get_order(context=context)
        _logger.debug("checkout values order : " + str(order))
        values.update(sale_order_obj._get_website_data(cr, uid, order, context))
        _logger.debug("checkout values : " + str(values))
        return values


        # cr, uid, context = request.cr, request.uid, request.context
        # context.update({'checkout' : True})
        # _logger.debug("Request for checkout page received")
        # order = request.website.sale_get_order(force_create=1, context=context)
        # #adapt when delivery method is changed
        # carrier_id = post.get('carrier_id')
        # if carrier_id:
        #     carrier_id = int(carrier_id)
        #     _logger.debug("carrierID : %d", carrier_id)
        # if order:
        #     _logger.debug("orderID : %d", order.id)
        #     request.registry['sale.order']._check_carrier_quotation(cr, uid, order, force_carrier_id=carrier_id, context=context)
        #     if carrier_id:
        #         return request.redirect("/shop/checkout")

        # redirection = self.checkout_redirection(order)
        # if redirection:
        #     _logger.debug("checkout : redirection")
        #     return redirection

        # values = self.checkout_values()
        # #need delivery informations #TODO : overload checkout_values instead of adding get_website_data
        # sale_order_obj = request.registry.get('sale.order')
        # values.update(sale_order_obj._get_website_data(cr, uid, order, context))
        # #need shipping informations of the shop
        # #order = request.website.sale_get_order(force_create=1, context=context)
        # _logger.debug("order.carrier_id : %d", order.carrier_id)
        # _logger.debug("order.carrier_id.name : %s", order.carrier_id.name)

        # return request.website.render("website_sale.checkout", values)
    
    def order_lines_2_google_api(self, order_lines):
        """ Transforms a list of order lines into a dict for google analytics """
        order_lines_not_delivery = [line for line in order_lines if not line.is_delivery]
        return super(website_sale, self).order_lines_2_google_api(order_lines_not_delivery)

    def checkout_values(self, data=None):
        values = super(website_sale, self).checkout_values(data)
        return request.env['sale.order']._get_shipping_country(values)

    def order_2_return_dict(self, order):
        """ Returns the tracking_cart dict of the order for Google analytics """
        ret = super(website_sale, self).order_2_return_dict(order)
        for line in order.order_line:
            if line.is_delivery:
                ret['transaction']['shipping'] = line.price_unit
        return ret
