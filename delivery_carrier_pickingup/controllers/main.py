# -*- coding: utf-8 -*-
import werkzeug

from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug
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

    #    

        
        values.update({'delivery_id' : order.carrier_id})
            #shipping info will be retrieved in view from delivery carrier
        
        return values