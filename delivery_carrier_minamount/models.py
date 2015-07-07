# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp
import logging
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)


class DeliveryCarrier(osv.osv):
    _name = "delivery.carrier"
    _inherit = "delivery.carrier"
    

    def get_price(self, cr, uid, ids, field_name, arg=None, context=None):
        """overload to add lower amount bound check"""
        res = super(DeliveryCarrier,self).get_price(cr, SUPERUSER_ID, ids, field_name, arg=arg, context=context)
        order_id=context.get('order_id',False)
        carrier_to_check_ids = [key for key in res.keys() if res[key]['available'] ]
        _logger.debug("Carriers_to_check : %s", str(carrier_to_check_ids))
        for carrier in self.browse(cr, SUPERUSER_ID, carrier_to_check_ids, context=context) :
            if carrier.not_available_if_less_than and order_id :
                order = self.pool.get('sale.order').browse(cr, SUPERUSER_ID, order_id, context=context)
                _logger.debug("Will check total")
                if carrier.amount_lower_bound > ((order.amount_total - order.amount_delivery) or 0.0) :
                    res[carrier.id]['available'] = False
        return res
    
    _columns = {
        'not_available_if_less_than' : fields.boolean(string='Not Available If Order Total Amount Is Less Than', help="If the order is less expensive than a certain amount, the customer can't benefit from this delivery method"),
        'amount_lower_bound' : fields.float(string='Minimum Amount', default=0, help="Amount of the order to benefit of this delivery method, expressed in the company currency"),
        'available' : fields.function(get_price, string='Available',type='boolean', multi='price',
            help="Is the carrier method possible with the current order.") #update function reference
    }
    
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