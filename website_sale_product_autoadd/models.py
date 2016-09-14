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
    
    def _delivery_unset(self, cr, uid, ids, context=None):
        #Overload to handle relational product with delivery product
        for so in self.browse(cr, SUPERUSER_ID, ids, context=context) :
            _logger.debug("looking after accompanying product to remove with delivery line")
            companions_quantities = {}
            for line in so.order_line :
                if line.is_delivery : #line to be removed in super call
                    _logger.debug("delivery line find")
                    for companion_product in line.product_id.companion_product_ids :
                        _logger.debug("companion product find : %s", companion_product.name)
                        companions_quantities[companion_product.id] = 0
        result = super(SaleOrder,self)._delivery_unset(cr,uid,ids, context=context)
        #we suppose only one SO
        for companion_id, companion_quantity in companions_quantities.iteritems() :
                _logger.debug("companion product to update, id : %s, quantity : %s", companion_id, companion_quantity)
                self._cart_update(cr, uid, ids, product_id=companion_id, set_qty=companion_quantity, add_qty=-1)
        
        #self.pool['sale.order']._cart_update(cr, uid,ids, context=context)
        return result
    
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
        if companions_quantities :
            result_dict['quantity'] = 0 #force reload whith json request
        return result_dict
    