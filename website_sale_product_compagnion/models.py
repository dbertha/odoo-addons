# -*- coding: utf-8 -*-

from functools import partial
from openerp import models, SUPERUSER_ID
from openerp import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class ProductCompanionPack(models.Model):
    _name = "product.companion.pack"
    name = fields.Char(string="Name", required = True)
    qty = fields.Float('Quantity', help="The quantity should be expressed in product uom",required=True)
    companion_product_product = fields.Many2one('product.product',
            string='Product', required=True,
            help='Those products will be automatically added/removed when the product is added/removed from the cart, with the correct quantity')
    


class ProductCompanionRule(models.Model):
    _name = "product.companion.rule"
    name = fields.Char(string="Name", required = True)
    qty_lower_bound = fields.Float('Quantity lower bound (included)', required=True)
    qty_upper_bound = fields.Float('Quantity upper bound (included)', required=True)
    companion_product_packs = fields.Many2many('product.companion.pack',
            'product_companion_rel','product_id','rule_id', required=True, string='Product packs to have in cart', 
            help='Those products will be automatically added/removed when the product is added/removed from the cart, with the correct quantity')
    

class ProductProduct(models.Model):
    #_name = 'product.public.category'
    _inherit = "product.product"
    companion_product_rules = fields.Many2many('product.companion.rule',
            'product_companion_rel','product_id','rule_id', string='Mandatory Accompanying products', 
            help='Those products will be automatically added/removed when the product is added/removed from the cart, with the correct quantity')
    
    @api.one
    def get_companion_packs(self, quantity) :
        pack_ids = []
        for rule in self.companion_product_rules :
            if rule.qty_lower_bound <= quantity <= rule.qty_upper_bound :
                pack_ids.extend(rule.companion_product_packs)
        return pack_ids

class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = "sale.order.line"
    companion_of_line_id = fields.Many2one('sale.order.line', string="Companion of this line")
    


    # @api.one
    # @api.constrains('end_hour', 'start_hour', 'end_min', 'start_min')
    # def _check_dates(self) :
    #     period = self
    #     if not (period.end_hour > period.start_hour) :
            
    #         if period.end_hour == period.start_hour :
    #             if period.end_min <= period.start_min :
    #                 raise ValidationError(_('The end of the period should be after the start.'))
    #         else : 
    #             raise ValidationError(_('The end of the period should be after the start.'))
    

    
    # _constraints = [
    #     (partial(osv.osv._check_m2m_recursion, field_name='companion_product_ids'), 
    #      'Error ! You cannot create recursive mandatory products.', ['companion_product_ids'])
    # ]

class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = "sale.order"

    @api.one
    def clear_companions(self, line_id=False) :
        self.order_line.filtered(lambda line : line.companion_of_line_id and (line.companion_of_line_id.id == line_id or not line_id)).unlink()

    @api.one
    def generate_companions(self, line_id=False) :
        context = dict(self.env.context)
        pack_ids = {}
        for line in ((not line_id and self.order_line) or self.order_line.filtered(lambda line : line.id == line_id)) :
            pack_ids[line.id] = line.product_id.get_companion_packs(line.product_uom_qty)
        context['companions'] = True
        for line_id, packs in pack_ids :
            for pack in packs :
                res = self.with_context(context)._cart_update(product_id=pack.companion_product_product.id, add_qty=pack.qty)
                self.env['sale.order.line'].browse(res['line_id']).companion_of_line_id = line_id

    @api.one
    def _cart_find_product_line(self,product_id=None, line_id=None, **kwargs):
        if self.env.context.get('companions', False) :
            return []
        else :
            return super(SaleOrder,self)._cart_find_product_line(product_id, line_id, **kwargs)

    @api.one
    def _delivery_unset(self):
        #Overload to handle relational product with delivery product
        line = self.order_line.filtered('is_delivery')
        result = super(SaleOrder,self)._delivery_unset()
        if not self.env.context.get('companions', False) and line :
            self.clear_companions(line.id)
            self.generate_companions(line.id)

        #self.pool['sale.order']._cart_update(cr, uid,ids, context=context)
        return result

    @api.multi
    def delivery_set(self):
        result = super(SaleOrder,self).delivery_set()
        for order in self :
            if not self.env.context.get('companions', False) :
                line = order.order_line.filtered('is_delivery')
                order.clear_companions(line.id)
                order.generate_companions(line.id)
        return result
    
    @api.one
    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        """Overload to remove delivery method when all leaving products are with a delivery condition with lower priority,
        because otherwise it will apply its delivery condition to the cart"""
        result_dict = super(SaleOrder,self)._cart_update(product_id, line_id, add_qty, set_qty)
        if not self.env.context.get('companions', False) :
            self.clear_companions(result_dict['line_id'])
            self.generate_companions(result_dict['line_id'])
        return result_dict



    #     companions_quantities_of_line = {}
    #     if line_id :
    #         line_before_update = self.pool.get('sale.order.line').browse(cr, SUPERUSER_ID, line_id, context=context)
    #         for companion_product in line_before_update.product_id.companion_product_ids :
    #             companions_quantities_of_line[companion_product.id] = 0
    #         _logger.debug("companions before update : %s", str(companions_quantities_of_line))
    #     result_dict = super(SaleOrder,self)._cart_update(cr, uid, ids, product_id, line_id, add_qty, set_qty, context=context)
    #     for so in self.browse(cr, SUPERUSER_ID, ids, context=context) :
    #         #companions_quantities = {}
    #         companions_quantities = {}
            
    #         if result_dict.get('quantity') == 0 :
    #             #line removed, product should still be checked
    #             #unlink : removed from line table or just from so ?
    #             if line_id :
    #                 _logger.debug("updating from before update")
    #                 companions_quantities.update(companions_quantities_of_line)
    #             elif product_id is not None :
    #                 for companion_product in \
    #                         self.pool.get('product.product').browse(cr,uid, product_id, context=context).companion_product_ids :
    #                     companions_quantities[companion_product.id] = companions_quantities.get(companion_product.id,0)
    #             else :
    #                 _logger.debug("Line lost")
                
    #         for so_line in so.order_line :
    #             for companion_product in so_line.product_id.companion_product_ids :
    #                 #TODO: what if uom quantity are not integers ? should be forbidden ?
    #                 _logger.debug("companion_id : %d", companion_product.id)
    #                 companions_quantities[companion_product.id] = companions_quantities.get(companion_product.id,0) + so_line.product_uom_qty
    #         _logger.debug("Companions to apply : %s", str(companions_quantities))
    #         for companion_id, companion_quantity in companions_quantities.iteritems() :
    #             #recursive call
    #             _logger.debug("Updating cart with companions products")
    #             #TODO : recursive call to itself should suppose a stop case : consider only the line modified
    #             super(SaleOrder,self)._cart_update(cr, uid, ids, product_id=companion_id, set_qty=companion_quantity, add_qty=-1)
    #             # add_qty in case of set_qty=0; because _cart_update test : "if set_qty"
    #     if companions_quantities :
    #         result_dict['quantity'] = 0 #force reload whith json request
    #     return result_dict
    # 