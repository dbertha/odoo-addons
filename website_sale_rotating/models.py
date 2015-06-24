# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp import models
from openerp.osv import osv, fields
from openerp.addons.web.http import request
import logging

_logger = logging.getLogger(__name__)
#TODO : superuser ID

class sale_configuration(osv.osv_memory):
    _inherit = 'sale.config.settings'

    _columns = {
        'current_week_number': fields.selection(
                [(1, 'Week 1'), (2, 'Week 2'), (3, 'Week 3'), (4, 'Week 4')],
                string="Current week number :",
                help="Choose the current week for rotating products.", 
            )
    }
    
    def set_current_week_number(self, cr, uid, ids, context=None):
        product_template_objs = self.pool['product.template']
        for record in self.browse(cr, uid, ids, context=context):
            product_template_objs.reset_week_published(cr, uid, [0], context=context)
            product_template_objs.publish_tagged_products(cr, uid, [0], record.current_week_number, context=context)
            
        
    def get_default_current_week_number(self, cr, uid, ids, context=None):
        product_template_objs = self.pool['product.template']
        current_week = product_template_objs.get_current_week(cr, uid, [0], context=None)
        return {'current_week_number': current_week or None}
    
class product_template(osv.Model):
    _inherit = 'product.template'
    
    _columns = {
        'week_number': fields.selection(
                [(1, 'Week 1'), (2, 'Week 2'), (3, 'Week 3'), (4, 'Week 4')],
                string="Number of the week of publication :",
                help="Choose the week when this product should be published. Left blank if not rotating", 
            )
    }
    
    def get_current_week(self, cr, uid, ids, context=None): 
        """Return week number whose articles are currently published.
        Assert : the published articles with a week number att have all the same week number
        """
        product_ids = self.search(cr, uid, [('website_published', '=', True)], context=context)
        for product in self.browse(cr, uid, product_ids, context=context) :
            _logger.debug("article tested : %s with number %s", product.name, str(product.week_number))
            if product.week_number :
                _logger.debug("current week found : %d", product.week_number)
                return product.week_number
        return False
    
    def reset_week_published(self, cr, uid, ids, context=None):
        """Set the published attribute of all products with a week number to False"""
        product_ids = self.search(cr, uid, [('website_published', '=', True)], context=context)
        for product in self.browse(cr, uid, product_ids, context=context) :
            if product.week_number :
                product.write({'website_published' : False})
    
    def publish_tagged_products(self, cr, uid, ids, weeknumber, context=None):
        """Set the published attribute of the product of that weeknumber to True"""
        product_ids = self.search(cr, uid, 
                            [('website_published', '=', False), ('week_number', '=', weeknumber)], context=context)
        _logger.debug("number of articles with week %d : %d", weeknumber, len(product_ids))
        for product in self.browse(cr, uid, product_ids, context=context) :
            product.write({'website_published' : True})
    
    def tick(self, cr, uid, ids=[0], context=None):
        """One tick in the rotation
        For good behavior, assert that there is a least one article for each of
        the possible week number (this is how we store the current week number)"""
        current_week = self.get_current_week(cr, uid, ids, context)
        _logger.debug("current week : %d", current_week)
        self.reset_week_published(cr, uid, ids, context)
        if(current_week):
            new_current_week = 1 + (current_week % 4) #1,2,3,4
            self.publish_tagged_products(cr, uid, ids, new_current_week, context)
            
    def onchange_week_number(self, cr, uid, ids, new_week_number, context=None):
        current_week = self.get_current_week(cr, uid, ids, context)
        _logger.debug("current week : %d, new week_number : %d", current_week, new_week_number)
        #week_number = None #TODO
        if(current_week == new_week_number) :
           return {'value': {
            'website_published': True,
        }}
        elif(new_week_number != 0) :
            _logger.debug("article should be unpublished")
            return {'value': {
            'website_published': False,
        }}
        return {'value': {}}
        
    def is_rotating(self, cr, uid, ids, context=None):
        """Expect only one ID"""
        for product in self.browse(cr, uid, ids, context=context) :
            return product.week_number
        
class delivery_condition(osv.Model):
    #TODO : incompatibility between categories but product can be from multiple categ : proper ?
    _name = "delivery.condition"
    _description = "Delivery Condition : delivery carrier and delays compatible"
     
    _columns = {
        'name': fields.char('Delivery Condition Name', required=True),
        #'partner_id': fields.many2one('res.partner', 'Transport Company', required=True, help="The partner that is doing the delivery service."),
        #'product_id': fields.many2one('product.product', 'Delivery Product', required=True),
        'category_ids': fields.one2many('product.public.category', 'condition_id', string='Public Categories'),
        #TODO : conditions_id : 'carrier_id': fields.many2one('delivery.carrier', 'Carrier', required=True, ondelete='cascade')
        'carrier_ids' : fields.one2many('delivery.carrier', 'condition_id', string='Delivery Carriers'),
        'delay_from' : fields.integer(string="Delay in days from the present as minimum date"),
        'delay_to' : fields.integer(string="Delay in days from the minimum date as maximum date"),
        'limit_to_a_range_of_days' : fields.boolean(
                        string="Delivery date proposition should be limited to the range",
                        help="Max and min dates will be computed from there and delay from"),
        'range_start' : fields.selection(
                [(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thurday'), 
                 (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')], #1-7 because no selection = 0
                string="First day of the allowed range"
                ),
    #fields.integer(string="First day of the allowed range (0-monday, 6-sunday)"),
        'range_end' : fields.selection(
                [(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thurday'), 
                 (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')], #1-7 because no selection = 0
                string="Last day of the allowed range"
                )
    #fields.integer(string="Last day of the allowed range (0-monday, 6-sunday)")
        #possible improvement : 'repeat_interval'
        #cas : 
        #normal : min = now + 1h
        #events : min = now + 1 day + 1 day if after 17h
        #FFY : samedi à mardi
    }
    #TODO : in a sale order, only one delivery_conditions represented
    #TODO : gestion propre du débordement de l'interval à la semaine suivante'
    
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
        'condition_id' : fields.many2one('delivery.condition', string="Conditions of Delivery")
    }
    
class sale_order(osv.osv):
    _name = "sale.order"
    _inherit = "sale.order"
    
    _columns = {
        'delivery_condition' : fields.related('order_line', 
            'product_id', 'product_tmpl_id', 'public_categ_ids', 'condition_id', 
            type="many2one", relation="delivery.condition", string="Delivery Condition")
    } 
    """this field will provide a link to the delivery condition of the first public categ of the first product
        Expect only one type of delivery condition in the sale order
        i.e. all the categories of the products in sale order lines have
        the same delivery condition"""
        
class Website(osv.osv):
    _inherit = 'website'
    
    def sale_product_domain(self, cr, uid, ids, context=None):
        """Remove objects from categories with another delivery condition than the sale order"""
        domain = super(Website, self).sale_product_domain(cr, uid, ids, context=context)
        sale_order_obj = self.pool['sale.order']
        sale_order_id = request.session.get('sale_order_id')
        _logger.debug("sale product domain overload")
        if sale_order_id :
            sale_order = sale_order_obj.browse(cr, SUPERUSER_ID, sale_order_id, context=context)  
            if sale_order.exists() :
                _logger.debug("sale order exists")
                if sale_order.delivery_condition :
                    #find the acceptable categs
                    categs_ids = self.pool['product.public.category'].search(cr,uid, 
                            [('condition_id', '=', sale_order.delivery_condition.id)], context=context)
                    
                    _logger.debug("sale order condition : %d", sale_order.delivery_condition.id)
                    domain += [('public_categ_ids','in',categs_ids)]
        return domain
    
#     def get_delivery_condition(self,cr,uid,order_id,context=None) :
#         """Expect only one type of delivery condition in the sale order
#         i.e. all the categories of the products in sale order lines have
#         the same delivery condition
#         Expect only one order_id"""
#         for order in self.browse(cr, uid, [order_id], context) :
#             for line in order.order_line :
#                 if line.product_id :
#                     public_categs =line.product_id.product_tmpl_id.public_categ_ids 
#                     if public_categs :
#                         return public_categs[0].condition_id
#                     