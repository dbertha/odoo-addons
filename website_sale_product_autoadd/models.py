# -*- coding: utf-8 -*-

from functools import partial
from openerp import models, SUPERUSER_ID
from openerp.osv import osv, fields
import logging

_logger = logging.getLogger(__name__)


class ProductProduct(osv.osv):
    #_name = 'product.public.category'
    _inherit = "product.product"
    _columns = {
        'companion_product_ids': fields.many2many('product.product',
            'product_companion_rel','src_id','dest_id', string='Mandatory Accompanying products', 
            help='Those products will be automatically added/removed when the product is added/removed from the cart, with the correct quantity')
    }
    
    _constraints = [
        (partial(osv.osv._check_m2m_recursion, field_name='companion_product_ids'), 
         'Error ! You cannot create recursive mandatory products.', ['companion_product_ids'])
    ]

class SaleOrder(osv.osv):
    _name = "sale.order"
    _inherit = "sale.order"
    
    def _cart_update(self, cr, uid, ids, product_id=None, line_id=None, add_qty=0, set_qty=0, context=None, **kwargs):
        """Overload to remove delivery method when all leaving products are with a delivery condition with lower priority,
        because otherwise it will apply its delivery condition to the cart"""
        companions_quantities_of_line = {}
        if line_id :
            line_before_update = self.pool.get('sale.order.line').browse(cr, SUPERUSER_ID, line_id, context=context)
            for companion_product in line_before_update.product_id.companion_product_ids :
                companions_quantities_of_line[companion_product.id] = 0
            _logger.debug("companions before update : %s", str(companions_quantities_of_line))
        result_dict = super(SaleOrder,self)._cart_update(cr, uid, ids, product_id, line_id, add_qty, set_qty, context=context)
        for so in self.browse(cr, SUPERUSER_ID, ids, context=context) :
            #companions_quantities = {}
            companions_quantities = {}
            
            if result_dict.get('quantity') == 0 :
                #line removed, product should still be checked
                #unlink : removed from line table or just from so ?
                if line_id :
                    _logger.debug("updating from before update")
                    companions_quantities.update(companions_quantities_of_line)
                elif product_id is not None :
                    for companion_product in \
                            self.pool.get('product.product').browse(cr,uid, product_id, context=context).companion_product_ids :
                        companions_quantities[companion_product.id] = companions_quantities.get(companion_product.id,0)
                else :
                    _logger.debug("Line lost")
                
            for so_line in so.order_line :
                for companion_product in so_line.product_id.companion_product_ids :
                    #TODO: what if uom quantity are not integers ? should be forbidden ?
                    _logger.debug("companion_id : %d", companion_product.id)
                    companions_quantities[companion_product.id] = companions_quantities.get(companion_product.id,0) + so_line.product_uom_qty
            _logger.debug("Companions to apply : %s", str(companions_quantities))
            for companion_id, companion_quantity in companions_quantities.iteritems() :
                #recursive call
                _logger.debug("Updating cart with companions products")
                #TODO : recursive call to itself should suppose a stop case : consider only the line modified
                super(SaleOrder,self)._cart_update(cr, uid, ids, product_id=companion_id, set_qty=companion_quantity, add_qty=-1)
                # add_qty in case of set_qty=0; because _cart_update test : "if set_qty"
        for so in self.browse(cr, SUPERUSER_ID, ids, context=context) :
            _logger.debug("Total after cart update : %d", so.amount_total)
#             delivery_conditions = {}
#             for so_line in so.order_line :
#                 if not so_line.is_delivery : #test other products (could also use website_order_line)
#                     for categ in so_line.product_id.product_tmpl_id.public_categ_ids :
#                     #handle properly categs of same product with different delivery_condition
#                         delivery_condition = categ.condition_id
#                         delivery_conditions.update({delivery_condition.sequence : delivery_condition.id})
#             result = delivery_conditions[min(delivery_conditions.keys())]
             
             
        if companions_quantities :
            result_dict['quantity'] = 0 #force reload whith json request
        return result_dict
    