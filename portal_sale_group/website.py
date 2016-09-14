# -*- coding: utf-8 -*-

from openerp import models, SUPERUSER_ID
from openerp.osv import osv, fields
import logging

_logger = logging.getLogger(__name__)

class website(osv.osv):
    _inherit = 'website'
    
    def sale_get_order(self, cr, uid, ids, force_create=False, code=None, update_pricelist=None, context=None) :
        """overload to mark sale order if portal group order"""
        order = super(website, self).sale_get_order(cr, uid, ids, force_create=force_create, code=code, update_pricelist=update_pricelist, context=context)
        if order :
            sale_order_obj = self.pool.get('sale.order')
            user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid, context=context)
            sale_order_obj = self.pool.get('sale.order')
            #updating group_id, user can be excluded from group
            _logger.debug("Writing user group id : %s", user.name)
            sale_order_obj.write(cr, SUPERUSER_ID, order.id, {'portal_group_id' : bool(user.portal_group_id) and user.portal_group_id.id}, context=context)
            _logger.debug("order portal group : %s", bool(user.portal_group_id) and user.portal_group_id.id)
            return sale_order_obj.browse(cr, SUPERUSER_ID, order.id, context=context)
        return order