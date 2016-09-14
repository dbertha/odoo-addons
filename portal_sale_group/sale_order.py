# -*- coding: utf-8 -*-

from openerp import models, SUPERUSER_ID
from openerp.osv import osv, fields
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(osv.osv) :
    _name = "sale.order"
    _inherit = "sale.order"
    
    _columns = {
        'portal_group_id' : fields.many2one('res.users.groups', string="Portal Group", readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    }
    
    def _get_sale_orders_with_group(self, cr, uid, ids, group_by,group_id, period_start, period_end, context=None) :
        if group_by == "portal_group_id" :
            search_domain = [('requested_delivery_datetime_start', '>=', period_start.strftime('%Y-%m-%d %H:%M:%S')), 
                    ('requested_delivery_datetime_start', '<', period_end.strftime('%Y-%m-%d %H:%M:%S')),
                    ('portal_group_id', '=', group_id)]
            _logger.debug("Search of SO to invoice domain : %s", search_domain)
            sale_order_obj = self.pool.get('sale.order')
            order_ids = sale_order_obj.search(cr,SUPERUSER_ID, search_domain, context=context)
            portal_group = self.pool.get('res.users.groups').browse(cr, SUPERUSER_ID, group_id, context=context)
            invoice_values = {
                'partner_id' : portal_group.administrator.partner_id.id,
                'origin' : u"{}/{}".format(portal_group.name, period_end.strftime('%d-%m-%Y'))
                }
            return order_ids, invoice_values
        return super(SaleOrder, self)._get_sale_orders_with_group(cr, uid, ids, group_by,group_id, period_start, period_end, context=context)

    
    def _get_delivery_methods(self, cr, uid, order, context=None) :
        """Overload in order to bypass delivery condition check of delivery method
        easier than create a delivery method with a product in a new public categ that have this delivery condition"""
        if order.portal_group_id :
            obj_data = self.pool.get('ir.model.data')
            tmp = obj_data.get_object_reference(cr, uid, 'portal_sale_group', 'delivery_group_carrier')
            if tmp :
                return [tmp[1]]
        return super(SaleOrder,self)._get_delivery_methods(cr, uid, order, context=context)
    
    def action_button_confirm(self, cr, uid, ids, context=None):
        """Substract amount to order from user's credit"""
        _logger.debug("In action button confirm overload")
        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid, context=context)
        _logger.debug("username : %s", user.name)
        if user.portal_group_id :
            order = self.browse(cr, SUPERUSER_ID, ids, context=context)
            assert order.portal_group_id.id == user.portal_group_id.id
            new_amount = user.available_amount - order.amount_total
            assert new_amount >= 0.0
            _logger.debug("Will write new amount : %s", str(new_amount))
            self.pool.get('res.users').write(cr, SUPERUSER_ID, uid, {'available_amount' : new_amount}, context=context)
        if isinstance(ids, (int, long)):
            ids = [ids]
        return super(SaleOrder, self).action_button_confirm(cr, SUPERUSER_ID, ids, context=context)
    
    def get_datetime_format(self, cr, uid, order, context=None) :
        """Remove time from datetimepicker"""
        if order.portal_group_id :
            return 'ddd DD/MM/YYYY' # %a %d/%m/%Y %H:%m
        return super(SaleOrder, self).get_datetime_format(cr, uid, order, context=None)
    
    def is_portal_order(self, cr, uid, ids, context=None) :
        """Expect only one id"""
        assert len(ids) == 1
        for order in self.browse(cr, uid, ids, context=context) :
            return bool(order.portal_group_id)
        
    def _get_delivery_condition(self, cr, uid, ids, field_name, arg, context=None):
        result = super(SaleOrder, self)._get_delivery_condition(cr, uid, ids, field_name=field_name, arg=arg, context=context)
        for so in self.browse(cr,uid,ids,context=context) :
            if so.portal_group_id :
                #group delivery condition over product delivery condition
                result[so.id] = so.portal_group_id.delivery_condition.id
        return result