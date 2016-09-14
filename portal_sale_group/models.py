# -*- coding: utf-8 -*-

from openerp import models, SUPERUSER_ID
from openerp.osv import osv, fields
import logging

from datetime import date, datetime, timedelta, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
import pytz

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
        'product_id' : fields.many2one('product.product', string='Service Product', help="This product will be added to the invoice"),
    }
    
    def create(self, cr, uid, vals, context=None) :
        """Overload to create delivery condition for the group"""
        if not vals.get('delivery_condition') :
            delivery_condition_obj = self.pool.get('delivery.condition')
            delivery_condition_vals = {
                'delay_from' : 0, #group order for at least the next day
                'limit_hour' : 10,
                'name' : vals.get('name') #delivery condition with same name
            }
            delivery_condition_id = delivery_condition_obj.create(cr, SUPERUSER_ID,delivery_condition_vals, context=context)
            vals['delivery_condition'] = delivery_condition_id
        return super(PortalGroup, self).create(cr, uid, vals, context=context)
    
    def invoice_portal_group(self, cr, uid, ids=[], context=None) :
        """create and send invoices to groups with confirmed sale orders not yet invoiced"""
        if context is None :
            context = {}
        today = date.today()
        period_end = today - timedelta(days=1) #to be sure the day is over
        #TEST
        #period_end = datetime.max
        #
        groups_id = ids or self.search(cr, SUPERUSER_ID, [], context=context)
        new_invoices = []
        sale_order_obj = self.pool.get('sale.order')
        for group in self.browse(cr, SUPERUSER_ID, groups_id, context=context) :
            order_ids = sale_order_obj.search(cr, uid, [('portal_group_id', '=', group.id), ('invoiced', '!=', True), ('state', 'not in', ['draft', 'cancel'])], context=context)
            if order_ids :
                period_start = min([datetime.strptime(order.requested_delivery_datetime_start,'%Y-%m-%d %H:%M:%S') for order in sale_order_obj.browse(cr, SUPERUSER_ID, order_ids, context=context)])
                if isinstance(period_start, str) :
                    period_start = datetime.strptime(period_start, '%Y-%m-%d %H:%M:%S')
                context.update({'period_start' : period_start,
                            'period_end' : period_end})
                _logger.debug("context before invoice creation : %s", context)
                new_invoice_id = sale_order_obj.create_grouped_invoice(cr,uid,ids,group_by='portal_group_id',group_id=group.id,
                                            period_start=period_start,period_end=period_end, 
                                            invoice_delivery=False,apply_discount=False, service_to_add=group.product_id, context=context)
                if new_invoice_id :
                    new_invoices.append(new_invoice_id)
        ir_model_data = self.pool.get('ir.model.data')
        template_id = ir_model_data.get_object_reference(cr, uid, 'portal_sale_group', 'email_template_portal_group_invoice')[1]
        for invoice_id in new_invoices :
            self.pool.get('email.template').send_mail(cr, uid, template_id, invoice_id, force_send=False, context=context)
            
    def update_credit(self, cr, uid, ids=[], context=None) :
        "Update credit of users. Period is defined by the period of the cron action"
        groups_id = ids or self.search(cr, SUPERUSER_ID, [], context=context)
        for group in self.browse(cr, SUPERUSER_ID, groups_id, context=context) :
            for user in group.members_ids :
                if user.credit_tag :
                    amount = user.available_amount
                    if user.credit_tag.reset :
                        amount = 0
                    amount += user.credit_tag.amount
                    self.pool.get('res.users').write(cr, SUPERUSER_ID, [user.id], {
                                        'available_amount' : amount}, context=context)
        
            
class CreditTag(osv.osv) :
    _name = 'account.credit.tag'
    
    _columns = {
        'name' : fields.char(string="Name", help="Name of this tag"),
        'amount' : fields.integer(string="Amount to credit to user", help="This amount will be added to user credit periodically"),
        'reset' : fields.boolean(string="Reset", default=1)
        }