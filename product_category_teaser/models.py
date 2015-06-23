# -*- coding: utf-8 -*-

from openerp import models
from openerp.osv import osv, fields
import logging

_logger = logging.getLogger(__name__)


class ProductPublicCategory(osv.osv):
    #_name = 'product.public.category'
    _inherit = "product.public.category"
    _columns = {
            'website_description' : fields.text(
                    translate = True, 
                    help="Description for the e-shop catalog",
                    string="Website Description")
    }
    