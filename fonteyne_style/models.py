# -*- coding: utf-8 -*-

from openerp import models
from openerp.osv import osv, fields
import logging
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)
# class fonteyne_style(models.Model):
#     _name = 'fonteyne_style.fonteyne_style'

#     name = fields.Char()

class sale_order(models.Model):

    _inherit = 'sale.order'

    def action_button_confirm(self, cr, uid, ids, context=None):
        """Pricelist with promo code has to be desactivated once there is one sale order confirmed with it"""
        return_value = super(sale_order, self).action_button_confirm(cr, uid, ids, context=context)
        so = self.browse(cr, SUPERUSER_ID, ids[0], context=context)
        pricelist =  so.pricelist_id
        if pricelist.code : #promo to use only once
            self.pool.get('product.pricelist').write(cr, SUPERUSER_ID, [pricelist.id], {'active' : False}, context=context)
        return return_value

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