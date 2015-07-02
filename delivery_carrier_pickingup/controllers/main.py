# -*- coding: utf-8 -*-
import werkzeug

from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug
from openerp.addons.web.controllers.main import login_redirect
import openerp.addons.website_sale_delivery_on_checkout.controllers.main
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone
import pytz
import logging

_logger = logging.getLogger(__name__)
class website_sale(openerp.addons.website_sale_delivery_on_checkout.controllers.main.website_sale):

    def checkout_values(self, data=None):
        """overload to add shipping partner relative to address of delivery_carrier"""
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        
        values = super(website_sale, self).checkout_values(data)
        
        _logger.debug("checkout value overload for delivery shipping address")
        order = request.website.sale_get_order(force_create=1, context=context) 
        #partner_id defined in this call
        if not data : #TODO : handle errors, overwrite only when needed
            shipping_id = 0
            if order.carrier_id and order.carrier_id.is_pickup \
                 and order.carrier_id.address_partner and order.carrier_id.address_partner.street :
                shipping_id = -1
                if order.partner_id : #can be public user
                    domain = [("parent_id", "=", order.partner_id.id), ('type', "=", 'delivery'), 
                             ('name', '=' ,order.carrier_id.address_partner.name)]
                    shipping_from_carrier_ids = registry['res.partner'].search(cr, SUPERUSER_ID, 
                                domain, context=context)
                        
                    values.update({'delivery_id' : order.carrier_id})
                    if shipping_from_carrier_ids :
                        #partner with delivery in that shop already exists
                        _logger.debug("shipping_from_carrier_ids : %s", shipping_from_carrier_ids)
                        shipping_id = shipping_from_carrier_ids[0]
                        #cannot create shipping partner here because the order partner_id can be public user
    #                 if shipping_id is None :
    #                     #create new partner with shipping info of the delivery method
    #                     shipping_info = {}
    #                     partner_lang = request.lang if request.lang in [lang.code for lang in request.website.language_ids] else None
    #                     if partner_lang:
    #                         shipping_info['lang'] = partner_lang
    # 
    #                     shipping_info['type'] = 'delivery'
    #                     shipping_info['parent_id'] = order.partner_id.id
    #                     shipping_info.update({
    #                             'name' : order.carrier_id.address_partner.name,
    #                             'street' : order.carrier_id.address_partner.street,
    #                             'street2' : order.carrier_id.address_partner.street2,  
    #                             'state_id' : order.carrier_id.address_partner.state_id and order.carrier_id.address_partner.state_id or 0,
    #                             'city' : order.carrier_id.address_partner.city,              
    #                             'country_id' : order.carrier_id.address_partner.country_id and order.carrier_id.address_partner.country_id.id or 0
    #                     })
    #                     shipping_id = registry['res.partner'].create(cr, SUPERUSER_ID, shipping_info, context)
            values['checkout']['shipping_id'] = shipping_id
            values['shipping_id']= shipping_id #erase old data
    #    

        
        values.update({'delivery_id' : order.carrier_id})
            #shipping info will be retrieved in view from delivery carrier
        
        return values