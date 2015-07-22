# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp import models
from openerp.osv import osv, fields
from openerp.addons.web.http import request

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import time
import pytz
from pytz import timezone

import logging

_logger = logging.getLogger(__name__)


        
class delivery_condition(osv.osv):
    _name = "delivery.condition"
    _description = "Delivery Condition : delivery carrier and delays compatible"
     
    _columns = {
        'name': fields.char('Delivery Condition Name', required=True),
        'category_ids': fields.one2many('product.public.category', 'condition_id', string='Public Categories',
                                        readonly=True),
        'carrier_ids' : fields.one2many('delivery.carrier', 'condition_id', string='Delivery Carriers',
                                        readonly=True),
        'delay_from' : fields.integer(string="Delay in days from the present as minimum date"),
        #'delay_to' : fields.integer(string="Delay in days from the minimum date as maximum date"),
        'limit_to_a_range_of_days' : fields.boolean(
                        string="Delivery date proposition should be limited to the range",
                        help="Only the first allowed range will be available for delivery"),
        'range_start' : fields.selection(
                [(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thurday'), 
                 (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')], #1-7 because no selection == 0
                string="First day of the allowed range"
                ),
    #fields.integer(string="First day of the allowed range (0-monday, 6-sunday)"),
        'range_end' : fields.selection(
                [(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thurday'), 
                 (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')], #1-7 because no selection == 0
                string="Last day of the allowed range"
                ),
        'website_description' : fields.text(string="Text for the website", translate=True),
        'sequence': fields.integer('Sequence', required=True, default=10,help="The sequence field is used to order the delivery conditions \
            from the lowest sequences to the higher ones. \
            The order is important because it determines the priority between the delivery conditions."),
        'limit_hour' : fields.selection(
                [(1, '01'), (2, '02'), (3, '03'), (4, '04'), 
                 (5, '05'), (6, '06'), (7, '08'), (8, '08'),
                 (9, '09'), (10, '10'), (11, '11'), (12, '12'), 
                 (13, '13'), (14, '14'), (15, '15'), (16, '16'),
                 (17, '17'), (18, '18'), (19, '19'), (20, '20'), 
                 (21, '21'), (22, '22'), (23, '23'), (24, '24')], default=17,   
                string="Last hour of day to allow delivery for the next day"
                ),
        #possible improvement : 'repeat_interval'
        #cas : 
        #normal : min = now + 1h
        #events : min = now + 1 day + 1 day if after 17h
        #FFY : samedi à mardi
    }
    _order = "sequence"
    
class product_public_category(osv.osv):
    _name = 'product.public.category'
    _inherit = "product.public.category"
    _columns = {
        'condition_id' : fields.many2one('delivery.condition', string="Conditions of Delivery")
    }
    
class delivery_carrier(osv.osv):
    _name = "delivery.carrier"
    _inherit = "delivery.carrier"
    _columns = {
        'condition_id' : fields.related('product_id','product_tmpl_id','public_categ_ids','condition_id', 
            type="many2one", relation="delivery.condition", string="Delivery Condition", readonly=True,
            help="This is the delivery condition of the public category of the delivery product")
        #'is_pickup' : fields.boolean(string='is a shop pick-up', 
        #    help='if activated, the address of delivery_method will be used as shipping address'),
        #'address_partner' : fields.many2one('res.partner', string="Address", help="Address to use as shipping address")
    }
    
class sale_order(osv.osv):
    _name = "sale.order"
    _inherit = "sale.order"
    
    
    def _get_delivery_condition(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for so in self.browse(cr,uid,ids,context=context) :
            delivery_conditions = {}
            for so_line in so.order_line :
                if not so_line.is_delivery : #ignore delivery product
                    for categ in so_line.product_id.product_tmpl_id.public_categ_ids :
                    #handle properly categs of same product with different delivery_condition
                        delivery_condition = categ.condition_id
                        delivery_conditions.update({delivery_condition.sequence : delivery_condition.id})
            result[so.id] = delivery_conditions and delivery_conditions[min(delivery_conditions.keys())] or False
        return result
    
    _columns = {
        'delivery_condition' : fields.function(_get_delivery_condition, 
            type="many2one", relation="delivery.condition", string="Delivery Condition", readonly=True,
            help="this field will provide a link to the delivery condition with \
            the highest priority of the products in the sale order")
    } 

    

    def get_min_date(self,cr,uid, order, forbidden_days=None, context=None) :
        #order = self.browse(cr, SUPERUSER_ID, order_id, context)
        delivery_condition = order.delivery_condition
        _logger.debug("In overloaded min_date\nDelivery condition : %s", str(delivery_condition))
        _logger.debug("user_id : %s", str(uid))
        if delivery_condition :
            tzone = timezone('Europe/Brussels')
            now = pytz.utc.localize(datetime.now()).astimezone(tzone)
            delta = timedelta(hours=1)
            min_date = now.replace(minute=59) + delta 
            _logger.debug("Delay from : %s", str(min_date))
            if delivery_condition.limit_hour and now.hour >= delivery_condition.limit_hour : #day is over
                    min_date += timedelta(days=1)
            if(delivery_condition.delay_from > 0) :
                min_date = min_date.replace(hour=0,minute=0)
                delta = timedelta(days=delivery_condition.delay_from)
                
                min_date += delta
                if forbidden_days is None : forbidden_days = self.get_forbidden_days(cr, uid, order, context)
                delta = timedelta(days=1)

                if forbidden_days :
                    start_of_range = (max(forbidden_days) + 1) % 7
                    if min_date.weekday() not in forbidden_days and min_date.weekday() != start_of_range :
                        #should start at the first day of the range
                        while(min_date.weekday() != start_of_range) :
                            min_date += delta
                while(len(forbidden_days) < 7 and (min_date.weekday() in forbidden_days)) :
                    min_date += delta
            _logger.debug("Min date for delivery : %s", str(min_date))
            return [min_date.year, min_date.month, min_date.day, min_date.hour, min_date.minute]
        return super(sale_order,self).get_min_date(cr,uid,order,forbidden_days=forbidden_days, context=context)
    #TODO : get sale_order from database only once in parent caller
    def get_forbidden_days(self,cr,uid, order, context=None) :
        #order = self.browse(cr, SUPERUSER_ID, order_id, context=context)
        delivery_condition = order.delivery_condition
        forbidden_days = super(sale_order,self).get_forbidden_days(cr,uid,order, context=context) 
        if delivery_condition :
            if(delivery_condition.range_start and delivery_condition.range_end) :
                #warning : encoded as 1-7, but 0-6 needed
                range_start = delivery_condition.range_start -1
                range_end = delivery_condition.range_end -1
                if(delivery_condition.range_end < delivery_condition.range_start) :
                    forbidden_days = [x for x in range(range_end+1, range_start)]
                else :
                    allowed_days = range(range_start, range_end+1)
                    forbidden_days += [x for x in range(7) if (x not in allowed_days)]
                _logger.debug('Forbidden days : %s', forbidden_days)
        return forbidden_days
    
    def get_max_date(self,cr,uid, order, min_date=None,forbidden_days=None, context=None) :
        #order = self.browse(cr, SUPERUSER_ID, order_id, context=context)
        delivery_condition = order.delivery_condition
        if delivery_condition :
            if(delivery_condition.range_start and delivery_condition.range_end) :
                #only the first range allowed
                forbidden_days = self.get_forbidden_days(cr, uid, order, context)
                if(forbidden_days) :
                    end_of_range = (min(forbidden_days) - 1) % 7
                    if min_date :
                        min_date = datetime(*min_date)
                    else :
                        min_date = datetime(*self.get_min_date(cr, uid, order, context=context))
                    delta = timedelta(days=1)
                    max_date = min_date
                    while(max_date.weekday() != end_of_range) :
                        max_date += delta
                    max_date += delta
                    _logger.debug("max_date weekday : %d", max_date.weekday())
                    return [max_date.year, max_date.month, max_date.day, max_date.hour, max_date.minute]
        return super(sale_order,self).get_max_date(cr,uid,order,min_date=min_date, forbidden_days=forbidden_days, context=context) 
    
    def _get_delivery_methods(self, cr, uid, order, context=None):
        """do not display delivery methods incompatible with sale order delivery condition"""
        carrier_obj = self.pool.get('delivery.carrier')
        search_domain = [('website_published','=',True)]
        if order.delivery_condition :
            search_domain += [('condition_id','=', order.delivery_condition.id)]
        _logger.debug("Looking for delivery conditions")
        _logger.debug("Order total : %s", order.amount_total)
        delivery_ids = carrier_obj.search(cr, SUPERUSER_ID, search_domain, context=context)
        
        # Following loop is done to avoid displaying delivery methods who are not available for this order
        # This can surely be done in a more efficient way, but at the moment, it mimics the way it's
        # done in delivery_set method of sale.py, from delivery module
        _logger.debug("Will remove unavailable delivery methods")
        for delivery_id in carrier_obj.browse(cr, SUPERUSER_ID, delivery_ids, context=dict(context, order_id=order.id)):
            if not delivery_id.available:
                delivery_ids.remove(delivery_id.id)
        return delivery_ids
    
    #Overload to add logging for debug
    def delivery_set(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('sale.order.line')
        grid_obj = self.pool.get('delivery.grid')
        carrier_obj = self.pool.get('delivery.carrier')
        acc_fp_obj = self.pool.get('account.fiscal.position')
        self._delivery_unset(cr, uid, ids, context=context)
        for order in self.browse(cr, uid, ids, context=context):
            grid_id = carrier_obj.grid_get(cr, uid, [order.carrier_id.id], order.partner_shipping_id.id)
            if not grid_id:
                raise osv.except_osv(_('No Grid Available!'), _('No grid matching for this carrier!'))

            if order.state not in ('draft', 'sent'):
                raise osv.except_osv(_('Order not in Draft State!'), _('The order state have to be draft to add delivery lines.'))

            grid = grid_obj.browse(cr, uid, grid_id, context=context)

            taxes = grid.carrier_id.product_id.taxes_id
            fpos = order.fiscal_position or False
            taxes_ids = acc_fp_obj.map_tax(cr, uid, fpos, taxes)
            #create the sale order line
            line_infos = {
                'order_id': order.id,
                'name': grid.carrier_id.name,
                'product_uom_qty': 1,
                'product_uom': grid.carrier_id.product_id.uom_id.id,
                'product_id': grid.carrier_id.product_id.id,
                'price_unit': grid_obj.get_price(cr, uid, grid.id, order, time.strftime('%Y-%m-%d'), context),
                'tax_id': [(6, 0, taxes_ids)],
                'is_delivery': True
            }
            _logger.debug("New delivery line : %s", str(line_infos))
            line_obj.create(cr, uid, line_infos, context=context)
            
            
    #this method is no longer usefull if delivey_condition of sale order ignore the delivery condition of delivery products

#     def _cart_update(self, cr, uid, ids, product_id=None, line_id=None, add_qty=0, set_qty=0, context=None, **kwargs):
#         """Overload to remove delivery method when all leaving products are with a delivery condition with lower priority,
#         because otherwise it will apply its delivery condition to the cart"""
#         return_val = super(sale_order,self)._cart_update(cr, uid, ids, product_id, line_id, add_qty, set_qty, context=context)
#         for so in self.browse(cr, uid, ids, context=context) :
# #             delivery_conditions = {}
# #             for so_line in so.order_line :
# #                 if not so_line.is_delivery : #test other products (could also use website_order_line)
# #                     for categ in so_line.product_id.product_tmpl_id.public_categ_ids :
# #                     #handle properly categs of same product with different delivery_condition
# #                         delivery_condition = categ.condition_id
# #                         delivery_conditions.update({delivery_condition.sequence : delivery_condition.id})
# #             result = delivery_conditions[min(delivery_conditions.keys())]
#             
#             
#             if(not len(so.website_order_line)) : #cart cleared
#                 so.write({'carrier_id': None})
#                 self._delivery_unset(cr, SUPERUSER_ID, [so.id], context=context)
#         return return_val
    
class Website(osv.osv):
    _inherit = 'website'
    
#     def sale_product_domain(self, cr, uid, ids, context=None):
#         """Remove objects from categories with another delivery condition than the sale order"""
#         domain = super(Website, self).sale_product_domain(cr, uid, ids, context=context)
#         delivery_condition = self.sale_get_delivery_condition(cr, uid, ids, context)
#                     #find the acceptable categs
#                     #TODO : not in the non acceptable may be more secure
#         if(delivery_condition) :
#             categs_ids = self.pool['product.public.category'].search(cr,uid, 
#                             [('condition_id', '=', delivery_condition.id)], context=context)
#                     
#             _logger.debug("sale order condition : %d", delivery_condition.id)
#             domain += [('public_categ_ids','in',categs_ids)]
#         return domain
    
    def sale_get_delivery_condition(self,cr,uid,ids, context=None) :
        _logger.debug("get_delivery_condition, user id : %s", str(uid))
        sale_order_obj = self.pool['sale.order']
        sale_order_id = request.session.get('sale_order_id')
        _logger.debug("sale get_delivery_condition")
        if sale_order_id :
            sale_order = sale_order_obj.browse(cr, SUPERUSER_ID, sale_order_id, context=context)  
            if sale_order.exists() :
                _logger.debug("sale order exists")
                if sale_order.delivery_condition :
                    return sale_order.delivery_condition
        return False
    
    def sale_is_product_compatible_with_cart(self, cr, uid, tpl_product_id, context=None) :
        """Can be overloaded to handle incompatibility between delivery conditions"""
        return True
    
#         delivery_condition = self.sale_get_delivery_condition(cr, uid, [0],context=context)
#         if(not delivery_condition) : 
#             _logger.debug("No delivery condition in the cart")
#             return not delivery_condition
#         _logger.debug("delive1ry condition_id in the cart : %d", delivery_condition.id)
#         template = self.pool['product.template'].browse(cr, uid, tpl_product_id, context=context)
#         public_categ = len(template.public_categ_ids) and template.public_categ_ids[0]
#         _logger.debug("public_categ : %s", str(public_categ))
#         product_condition_id = public_categ and public_categ.condition_id and public_categ.condition_id.id
#         _logger.debug("production_condition_id : %s", str(product_condition_id))
#         return product_condition_id and delivery_condition.id == product_condition_id
