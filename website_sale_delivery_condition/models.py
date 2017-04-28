# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp import api, fields, models, _

from openerp.addons.web.http import request

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import time
import pytz
from pytz import timezone
import openerp.addons.decimal_precision as dp


import logging

_logger = logging.getLogger(__name__)


        
class DeliveryCondition(models.Model):
    _name = "delivery.condition"
    _description = "Delivery Condition : delivery carrier and delays compatible"
    
    # def _get_carrier_ids(self, cr, uid, ids, field_name, arg, context=None) :
    #     """Return the list of carriers with this delivery condition"""
    #     res = {}
    #     for condition in self.browse(cr, uid, ids, context=context):
    #         carrier_ids = self.pool.get('delivery.carrier').search(cr, uid, [('condition_ids', 'in', [condition.id])])
    #         res[condition.id] = carrier_ids
    #     return res
    
    name = fields.Char('Delivery Condition Name', required=True)
    category_ids = fields.One2many('product.public.category', 'condition_id', string='Public Categories',
                                        readonly=True)
    # Many2many inverse relation
    carrier_ids = fields.Many2many('delivery.carrier', string='Carriers', readonly=True)

    delay_from = fields.Integer(string="Delay in days from the present as minimum date")
        #'delay_to' : fields.integer(string="Delay in days from the minimum date as maximum date"),
    limit_to_a_range_of_days = fields.Boolean(
                        string="Delivery date proposition should be limited to the range",
                        help="Only the first allowed range will be available for delivery")
    range_start = fields.Selection(
                [(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thurday'), 
                 (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')], #1-7 because no selection == 0
                string="First day of the allowed range"
                )
    #fields.integer(string="First day of the allowed range (0-monday, 6-sunday)"),
    range_end = fields.Selection(
                [(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thurday'), 
                 (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')], #1-7 because no selection == 0
                string="Last day of the allowed range"
                )
    website_description = fields.Char(string="Text for the website", translate=True)
    sequence = fields.Integer('Sequence', required=True, default=10,help="The sequence field is used to order the delivery conditions \
            from the lowest sequences to the higher ones. \
            The order is important because it determines the priority between the delivery conditions.")
    limit_hour = fields.Selection(
                [(1, '01'), (2, '02'), (3, '03'), (4, '04'), 
                 (5, '05'), (6, '06'), (7, '08'), (8, '08'),
                 (9, '09'), (10, '10'), (11, '11'), (12, '12'), 
                 (13, '13'), (14, '14'), (15, '15'), (16, '16'),
                 (17, '17'), (18, '18'), (19, '19'), (20, '20'), 
                 (21, '21'), (22, '22'), (23, '23'), (24, '24')], default=17,   
                string="Last hour of day to allow delivery for the next day"
                )

    enterprise_portal_published = fields.Boolean(
                        string="Available on Enterprise Portal"
                        )

        # 'image': fields.binary("Image",
            # help="This field holds the image used as image for the shop page, limited to 1024x1024px.")
        #possible improvement : 'repeat_interval'
    
    _order = "sequence"
    
class ProductPublicCategory(models.Model):
    _name = 'product.public.category'
    _inherit = "product.public.category"

    condition_id = fields.Many2one('delivery.condition', string="Conditions of Delivery")
    
    
class DeliveryCarrier(models.Model):
    _name = "delivery.carrier"
    _inherit = "delivery.carrier"
    # condition_id = fields.related('product_id','product_tmpl_id','public_categ_ids','condition_id', 
    #         type="many2one", relation="delivery.condition", string="Delivery Condition", readonly=True,
    #         help="This is the delivery condition of the public category of the delivery product"),
    condition_ids = fields.Many2many('delivery.condition', 'delivery_carrier_condition_rel', 'carrier_id', 'condition_id',
                                           string="Delivery Conditions", 
                                           help="That delivery method will be available for order with one of those delivery condition.")
        #The delivery product should be in a category linked with the delivery condition with the lowest priority"),
        #Not true, because sale order delivery condition is not dependent of delivery lines
    
    @api.one
    def get_price(self):
        """overload to add delivery condition check"""
        res = super(DeliveryCarrier,self).get_price()
        order_id = self.env.context.get('order_id')
        if self.available and order_id :
            SaleOrder = self.env['sale.order']
            order = SaleOrder.sudo().browse(order_id)
            if order.delivery_condition and order.delivery_condition.id not in self.condition_ids.ids :
                self.available = False
            elif self.env.user.specific_delivery_price is not False : 
            #we should accept 0 #TODO : check if False or None when the column is set to NULL
                _logger.debug("specific delivery price : %s", self.env.user.specific_delivery_price)
                self.price = self.env.user.specific_delivery_price
        return res
    
    
class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = "sale.order"
    
    @api.multi
    def has_delivery_condition_named(self,delivery_name) :
        self.ensure_one()
        _logger.debug("Has delivery condition : start, delivery name : %s", delivery_name)
        return self.delivery_condition.name == delivery_name
    
    # def _get_delivery_condition(self, cr, uid, ids, field_name, arg, context=None) :
    #     result = {}
    #     for so in self.browse(cr,uid,ids,context=context) :
    #         delivery_conditions = {}
    #         for so_line in so.order_line :
    #             if not so_line.is_delivery : #ignore delivery product
    #                 for categ in so_line.product_id.product_tmpl_id.public_categ_ids :
    #                 #handle properly categs of same product with different delivery_condition
    #                     delivery_condition = categ.condition_id
    #                     delivery_conditions.update({delivery_condition.sequence : delivery_condition.id})
    #         result[so.id] = delivery_conditions and delivery_conditions[min(delivery_conditions.keys())] or False
    #     return result
    
    delivery_condition = fields.Many2one('delivery.condition', string="Conditions of Delivery")
    

    
    @api.multi
    def get_min_date(self,forbidden_days=None) :
        #order = self.browse(cr, SUPERUSER_ID, order_id, context)
        self.ensure_one()
        delivery_condition = self.delivery_condition
        _logger.debug("In overloaded min_date\nDelivery condition : %s", str(delivery_condition))
        _logger.debug("user_id : %s", str(self.env.uid))
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
        return super(SaleOrder,self).get_min_date(forbidden_days=forbidden_days)

    @api.multi
    def get_forbidden_days(self) :
        #order = self.browse(cr, SUPERUSER_ID, order_id, context=context)
        self.ensure_one()
        delivery_condition = self.delivery_condition
        forbidden_days = super(SaleOrder,self).get_forbidden_days() 
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
    
    @api.multi
    def get_max_date(self,min_date=None,forbidden_days=None) :
        self.ensure_one()
        #order = self.browse(cr, SUPERUSER_ID, order_id, context=context)
        delivery_condition = self.delivery_condition
        if delivery_condition :
            if(delivery_condition.range_start and delivery_condition.range_end) :
                #only the first range allowed
                forbidden_days = forbidden_days or self.get_forbidden_days()
                if(forbidden_days) :
                    end_of_range = (min(forbidden_days) - 1) % 7
                    if min_date :
                        min_date = datetime(*min_date)
                    else :
                        min_date = datetime(*self.get_min_date(forbidden_days=forbidden_days))
                    delta = timedelta(days=1)
                    max_date = min_date
                    while(max_date.weekday() != end_of_range) :
                        max_date += delta
                    max_date += delta
                    _logger.debug("max_date weekday : %d", max_date.weekday())
                    return [max_date.year, max_date.month, max_date.day, max_date.hour, max_date.minute]
        return super(SaleOrder,self).get_max_date(min_date=min_date, forbidden_days=forbidden_days) 
    
    # def _get_delivery_methods(self, cr, uid, order, context=None):
    #     """do not display delivery methods incompatible with sale order delivery condition"""
    #     carrier_obj = self.pool.get('delivery.carrier')
    #     search_domain = [('website_published','=',True)]
    #     if order.delivery_condition :
    #         search_domain += [('condition_ids','in', [order.delivery_condition.id])]
    #     delivery_ids = carrier_obj.search(cr, SUPERUSER_ID, search_domain, context=context)
        
    #     # Following loop is done to avoid displaying delivery methods who are not available for this order
    #     # This can surely be done in a more efficient way, but at the moment, it mimics the way it's
    #     # done in delivery_set method of sale.py, from delivery module
    #     _logger.debug("Will remove unavailable delivery methods")
    #     for delivery_id in carrier_obj.browse(cr, SUPERUSER_ID, delivery_ids, context=dict(context, order_id=order.id)):
    #         if not delivery_id.available:
    #             delivery_ids.remove(delivery_id.id)
    #     return delivery_ids
    
    # #Overload to add logging for debug and pass context
    # def delivery_set(self, cr, uid, ids, context=None):
    #     line_obj = self.pool.get('sale.order.line')
    #     grid_obj = self.pool.get('delivery.grid')
    #     carrier_obj = self.pool.get('delivery.carrier')
    #     acc_fp_obj = self.pool.get('account.fiscal.position')
    #     self._delivery_unset(cr, uid, ids, context=context)
    #     for order in self.browse(cr, uid, ids, context=context):
    #         grid_id = carrier_obj.grid_get(cr, uid, [order.carrier_id.id], order.partner_shipping_id.id, context=context)
    #         if not grid_id:
    #             raise osv.except_osv(_('No Grid Available!'), _('No grid matching for this carrier!'))

    #         if order.state not in ('draft', 'sent'):
    #             raise osv.except_osv(_('Order not in Draft State!'), _('The order state have to be draft to add delivery lines.'))

    #         grid = grid_obj.browse(cr, uid, grid_id, context=context)

    #         taxes = grid.carrier_id.product_id.taxes_id
    #         fpos = order.fiscal_position or False
    #         taxes_ids = acc_fp_obj.map_tax(cr, uid, fpos, taxes)
    #         #create the sale order line
    #         line_infos = {
    #             'order_id': order.id,
    #             'name': grid.carrier_id.name,
    #             'product_uom_qty': 1,
    #             'product_uom': grid.carrier_id.product_id.uom_id.id,
    #             'product_id': grid.carrier_id.product_id.id,
    #             'price_unit': grid_obj.get_price(cr, uid, grid.id, order, time.strftime('%Y-%m-%d'), context),
    #             'tax_id': [(6, 0, taxes_ids)],
    #             'is_delivery': True
    #         }
    #         _logger.debug("New delivery line : %s", str(line_infos))
    #         line_obj.create(cr, uid, line_infos, context=context)
            
            

    
class Website(models.Model):
    _inherit = 'website'
    

    def sale_get_delivery_condition(self) :
        _logger.debug("get_delivery_condition, user id : %s", str(self.env.uid))
        sale_order = self.sale_get_order(force_create=1)
        if sale_order.exists() :
            _logger.debug("sale order exists")
            if sale_order.delivery_condition :
                return sale_order.delivery_condition
        return False
    
    def sale_is_product_compatible_with_cart(self,tpl_product_id) :
        """Can be overloaded to handle incompatibility between delivery conditions"""
        condition = self.sale_get_delivery_condition()
        product = self.env['product.template'].browse(tpl_product_id)
        return not condition or ( condition.id in 
                        product.mapped('public_categ_ids').mapped('condition_id').mapped('id') )
    
    def sale_product_domain(self):
        # remove product event from the website content grid and list view (not removed in detail view)
        res = super(Website, self).sale_product_domain()
        delivery_condition = self.sale_get_delivery_condition()
        if delivery_condition :
            return ['&'] + res + [('public_categ_ids', 'child_of', delivery_condition.category_ids.ids)]
        return res


class ResUsers(models.Model):
    _inherit = 'res.users'
    

    enterprise_portal = fields.Boolean(
                        string="Enterprise Portal",
                        help="If loggued, will access to the enterprise website")
    specific_delivery_price = fields.Float(string='Fixed delivery price', digits=dp.get_precision('Product Price'))


        