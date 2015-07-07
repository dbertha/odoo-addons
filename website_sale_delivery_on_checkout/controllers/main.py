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
        cr, uid, context = request.cr, request.uid, request.context
        _logger.debug("Request for checkout page received")
        order = request.website.sale_get_order(force_create=1, context=context)
        #adapt when delivery method is changed
        carrier_id = post.get('carrier_id')
        if carrier_id:
            carrier_id = int(carrier_id)
            _logger.debug("carrierID : %d", carrier_id)
        if order:
            _logger.debug("orderID : %d", order.id)
            request.registry['sale.order']._check_carrier_quotation(cr, uid, order, force_carrier_id=carrier_id, context=context)
            if carrier_id:
                return request.redirect("/shop/checkout")

        redirection = self.checkout_redirection(order)
        if redirection:
            _logger.debug("checkout : redirection")
            return redirection

        values = self.checkout_values()
        #need delivery informations #TODO : overload checkout_values instead of adding get_website_data
        sale_order_obj = request.registry.get('sale.order')
        values.update(sale_order_obj._get_website_data(cr, uid, order, context))
        #need shipping informations of the shop
        #order = request.website.sale_get_order(force_create=1, context=context)
        _logger.debug("order.carrier_id : %d", order.carrier_id)
        _logger.debug("order.carrier_id.name : %s", order.carrier_id.name)
#         if(order.carrier_id) :
#             if(order.carrier_id.name.find("Tong") != -1) :
#                 _logger.debug("Adding Tongres address")
#                 values['checkout']['shipping_id'] = -1
#                 values['checkout']['shipping_name'] = "Tongres"
#                 values['checkout']['shipping_phone'] = "02 734 08 02"
#                 values['checkout']['shipping_street'] = "107, Rue Gérard"
#                 values['checkout']['shipping_city'] = "Etterbeek"
#                 values['checkout']['shipping_zip'] = "1040"
#                 values['checkout']['shipping_country_id'] = 21
#             elif(order.carrier_id.name.find("Wolu") != -1) :
#                 _logger.debug("Adding Wolu address")
#                 values['checkout']['shipping_id'] = -1
#                 values['checkout']['shipping_name'] = "Woluwé"
#                 values['checkout']['shipping_phone'] = "02 763 48 93"
#                 values['checkout']['shipping_street'] = "27, Avenue Baron d'Huart"
#                 values['checkout']['shipping_city'] = "Woluwé-Saint-Pierre"
#                 values['checkout']['shipping_zip'] = "1150"
#                 values['checkout']['shipping_country_id'] = 21
#             elif(order.carrier_id.name.find("Jaco") != -1) :
#                 _logger.debug("Adding Uccle address")
#                 values['checkout']['shipping_id'] = -1
#                 values['checkout']['shipping_name'] = "Uccle"
#                 values['checkout']['shipping_phone'] = "02 375 48 75"
#                 values['checkout']['shipping_street'] = "1395, Chaussée de Waterloo"
#                 values['checkout']['shipping_city'] = "Uccle"
#                 values['checkout']['shipping_zip'] = "1180"
#                 values['checkout']['shipping_country_id'] = 21
#             elif(order.carrier_id.name.find("ulpe") != -1) :
#                 _logger.debug("Adding La Hulpe address")
#                 values['checkout']['shipping_id'] = -1
#                 values['checkout']['shipping_name'] = "La Hulpe"
#                 values['checkout']['shipping_phone'] = " 02 652 21 93"
#                 values['checkout']['shipping_street'] = "30, Avenue Albert 1er"
#                 values['checkout']['shipping_city'] = "Genval"
#                 values['checkout']['shipping_zip'] = "1332"
#                 values['checkout']['shipping_country_id'] = 21
        return request.website.render("website_sale.checkout", values)
    
    def order_lines_2_google_api(self, order_lines):
        """ Transforms a list of order lines into a dict for google analytics """
        order_lines_not_delivery = [line for line in order_lines if not line.is_delivery]
        return super(website_sale, self).order_lines_2_google_api(order_lines_not_delivery)
    
    #overriding for testing
    
    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True)
    def confirm_order(self, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry

        order = request.website.sale_get_order(context=context)
        if not order:
            return request.redirect("/shop")
        #
        carrier_id = order.carrier_id.id
        _logger.debug("order total in confirm order beginning : %d", order.amount_total)
        #
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        values = self.checkout_values(post)
        _logger.debug("order total in confirm order after checkout values : %d", order.amount_total)
        if (post.get('shipping_name')) : 
            #needed to check delivery date depending on delivery method
            values["checkout"]['shipping_name'] = post.get('shipping_name')
        values["error"] = self.checkout_form_validate(values["checkout"])
        
        
        if values["error"]:
            #need delivery informations
            sale_order_obj = request.registry.get('sale.order')
            values.update(sale_order_obj._get_website_data(cr, uid, order, context))
            return request.website.render("website_sale.checkout", values)
        self.checkout_form_save(values["checkout"]) 
        
        order = request.website.sale_get_order(context=context)
        _logger.debug("order total in confirm order after checkout save : %d", order.amount_total)
        request.session['sale_last_order_id'] = order.id
                
        
        request.website.sale_get_order(update_pricelist=True, context=context)
        order = request.website.sale_get_order(context=context)
        _logger.debug("order total in confirm order after update_pricelist : %d", order.amount_total)
        #check carrier quotation should be called after sale get order with update pricelist
        request.registry['sale.order']._check_carrier_quotation(cr, uid, order, force_carrier_id=carrier_id, context=context)
        order = request.website.sale_get_order(context=context)
        _logger.debug("order total in confirm order after carrier quotation : %d", order.amount_total)
        
        return request.redirect("/shop/payment")