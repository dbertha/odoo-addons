# -*- coding: utf-8 -*-

from openerp import models, SUPERUSER_ID
from openerp.osv import osv, fields
import logging

_logger = logging.getLogger(__name__)



class PortalGroup(osv.osv) :
    _name = 'res.users.groups'
    
    def _compute_nb_of_members(self, cr, uid, ids, field_name, arg=None, context=None) :
        res = {}
        for group in self.browse(cr, SUPERUSER_ID, ids, context=context) :
            res[group.id] = len(group.members_ids)
        return res
    
    def _get_filtered_orders(self, cr, uid, ids, field_name, arg, context=None):
        """Return the list of orders with a correct state"""
        res = {}
        for group in self.browse(cr, uid, ids, context=context):
            so_ids = self.pool.get('sale.order').search(cr, uid, [('portal_group_id', '=', group.id), ('state', 'not in', ['draft', 'cancel'])])
            res[group.id] = so_ids
        return res
    
    _columns = {
        'name' : fields.char(string="Name", help="Name of the group", required=True),
        'members_ids' : fields.one2many('res.users', 'portal_group_id', string="Users", help="The users in the group"),
        'nb_of_members' : fields.function(_compute_nb_of_members, store=True, type='integer', string="Number of members"),
        'administrator' : fields.many2one('res.users', string="Administrator", help="Member of the group who can add and remove members"),
        'order_ids' : fields.one2many('sale.order', 'portal_group_id', string="Orders", help="The orders from users in the group", readonly=True),
        'filtered_order_ids' : fields.function(_get_filtered_orders,obj='sale.order', type="one2many", string="Orders", help="The orders from users in the group"),
        'delivery_condition' : fields.many2one('delivery.condition', string="Conditions of Delivery", ondelete="restrict"),
        'hour_of_delivery' : fields.selection([(9, "09"), (10,"10"), (11, "11"), (12, "12"), (13, "13"), (14, "14"), (15, "15")], default=10, required=True, string="Hour of delivery"),
        'product_id' : fields.many2one('product.product', string='Service Product', help="This product will be added to the invoice")
    }
    
    def create(self, cr, uid, vals, context=None) :
        """Overload to create delivery condition for the group"""
        if not vals.get('delivery_condition') :
            delivery_condition_obj = self.pool.get('delivery.condition')
            delivery_condition_vals = {
                'delay_from' : 1, #group order for at least the next day
                'name' : vals.get('name') #delivery condition with same name
            }
            delivery_condition_id = delivery_condition_obj.create(cr, SUPERUSER_ID,delivery_condition_vals, context=context)
            vals['delivery_condition'] = delivery_condition_id
        return super(PortalGroup, self).create(cr, uid, vals, context=context)
            