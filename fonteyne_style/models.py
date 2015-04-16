# -*- coding: utf-8 -*-

from openerp.osv import orm, fields
import logging

_logger = logging.getLogger(__name__)
# class fonteyne_style(models.Model):
#     _name = 'fonteyne_style.fonteyne_style'

#     name = fields.Char()

class ProductCategory(orm.Model):
    _inherit = 'product.category'
    
    def hierarchy_selected(self, cr, uid, ids, activeCategoryNumber, context=None):
        _logger.debug("hierarchy selected, number : %d", activeCategoryNumber)
        if not isinstance(activeCategoryNumber, int) :
            return False
                                                     
        for category in self.browse(cr, uid, ids, context=context) :
            if category.id == activeCategoryNumber : 
                return True
            else :
                return any(child.id == activeCategoryNumber for child in category.child_id)