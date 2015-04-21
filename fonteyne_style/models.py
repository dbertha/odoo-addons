# -*- coding: utf-8 -*-

from openerp import models
from openerp.osv import osv, fields
import logging

_logger = logging.getLogger(__name__)
# class fonteyne_style(models.Model):
#     _name = 'fonteyne_style.fonteyne_style'

#     name = fields.Char()

class ProductPublicCategory(osv.osv):
    #_name = 'product.public.category'
    _inherit = "product.public.category"
    
    def hierarchy_selected(self, cr, uid, ids, activeCategoryNumber, context=None):
        _logger.debug("hierarchy selected, number : %d", activeCategoryNumber)
        if not isinstance(activeCategoryNumber, int) :
            return False
                                                     
        for category in self.browse(cr, uid, ids, context=context) :
            if category.id == activeCategoryNumber : 
                return True
            else :
                if any(child.id == activeCategoryNumber for child in category.child_id) :
                    return True
        return False