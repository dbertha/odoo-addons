# -*- coding: utf-8 -*-

import openerp.addons.decimal_precision as dp
import logging
from openerp import models, fields, SUPERUSER_ID, api, _

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _name = "delivery.carrier"
    _inherit = "delivery.carrier" 
    
    @api.one
    def get_price(self):
        """overload to add lower amount bound check"""
        res = super(DeliveryCarrier,self).get_price()
        order_id = self.env.context.get('order_id')
        if self.available and self.not_available_if_less_than and order_id :
            SaleOrder = self.env['sale.order']
            order = SaleOrder.browse(order_id)

            if carrier.amount_lower_bound > ((order.amount_total - order.amount_delivery) or 0.0) :
                self.available = False

    
    not_available_if_less_than = fields.Boolean(string='Not Available If Order Total Amount Is Less Than', help="If the order total (except delivery costs) is less than the amount, the customer can't choose this delivery method")
    amount_lower_bound = fields.Float(string='Minimum Amount', default=0, help="Amount of the order to benefit of this delivery method, expressed in the company currency")
    
    
# class SaleOrder(osv.osv):
#     _name = "sale.order"
#     _inherit = "sale.order"
#     
#     def _get_amount_without_delivery(self, cr, uid, ids, field_name, arg, context=None) :
#         cur_obj = self.pool.get('res.currency')
#         res = {}
#         for order in self.browse(cr, uid, ids, context=context):
#             res[order.id] = {'amount_total_without_delivery' : 0.0}
#             val = val1 = 0.0
#             cur = order.pricelist_id.currency_id
#             for line in order.order_line:
#                 if not line.is_delivery :
#                     val1 += line.price_subtotal
#                     val += self._amount_line_tax(cr, uid, line, context=context)
#             amount_tax = cur_obj.round(cr, uid, cur, val)
#             amount_untaxed = cur_obj.round(cr, uid, cur, val1)
#             res[order.id]['amount_total_without_delivery'] = amount_tax + amount_untaxed
#         return res
#     
#     columns = {
#         'amount_total_without_delivery' : fields.function(_get_amount_without_delivery, digits_compute=dp.get_precision('Account'), string='Total Without Delivery')
#     }