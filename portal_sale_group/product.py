# -*- coding: utf-8 -*-

from openerp import models, SUPERUSER_ID
from openerp.osv import osv, fields
import logging

_logger = logging.getLogger(__name__)

class ProductTemplate(osv.osv) :
    _name = 'product.template'
    _inherit = 'product.template'
    
    _columns = {
        'is_available_for_group_orders' : fields.boolean(string="Group Order Availability", 
                help="Check if this product should be available for portal group orders")
    }
    
    _defaults = {
        'is_available_for_group_orders' : 1
    }