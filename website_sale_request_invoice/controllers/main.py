# -*- coding: utf-8 -*-
import werkzeug

from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug
from openerp.addons.web.controllers.main import login_redirect
import openerp.addons.website_sale.controllers.main
import logging


_logger = logging.getLogger(__name__)

class website_sale(openerp.addons.website_sale.controllers.main.website_sale):
    
    def checkout_values(self, data=None):
        """Overload to add delivery date parsing"""
        values = super(website_sale, self).checkout_values(data)
        if data :
            values['checkout'].update({'accept_invoice' : bool(data.get('accept_invoice', False))})
        return values
    
    def checkout_form_save(self, checkout):
        """overload to store accept invoice checkbox"""
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry

        partner_obj = registry.get('res.partner')
        
        super(website_sale, self).checkout_form_save(checkout)

        order = request.website.sale_get_order(context=context)
        
        _logger.debug("checkout form save, accept_invoice : %s", checkout.get('accept_invoice', False))
        partner_info = {'accept_invoice' : checkout.get('accept_invoice', False)}
        
        partner_obj.write(cr, SUPERUSER_ID, [order.partner_id.id], partner_info, context=context)