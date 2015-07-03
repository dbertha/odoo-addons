# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
import logging

_logger = logging.getLogger(__name__)


class delivery_carrier(osv.osv):
    _name = "delivery.carrier"
    _inherit = "delivery.carrier"
    

    def get_price(self, cr, uid, ids, field_name, arg=None, context=None):
        """overload to add lower amount check"""
        res = super(delivery_carrier,self).get_price(cr, uid, ids, field_name, arg=arg, context=context)
        order_id=context.get('order_id',False)
        carrier_to_check_ids = [key for key in res.keys() if res[key]['available'] ]
        _logger.debug("Carriers_to_check : %s", str(carrier_to_check_ids))
        for carrier in self.browse(cr, uid, carrier_to_check_ids, context=context) :
            if carrier.not_available_if_less_than and order_id :
                order = self.pool.get('sale.order').browse(cr, uid, order_id, context=context)
                _logger.debug("Will check total")
                if carrier.amount_lower_bound > (order.amount_total or 0.0) :
                    res[carrier.id]['available'] = False
        return res
    
    _columns = {
        'not_available_if_less_than' : fields.boolean(string='Not Available If Order Total Amount Is Less Than', help="If the order is less expensive than a certain amount, the customer can't benefit from this delivery method"),
        'amount_lower_bound' : fields.float(string='Minimum Amount', default=0, help="Amount of the order to benefit of this delivery method, expressed in the company currency"),
        'available' : fields.function(get_price, string='Available',type='boolean', multi='price',
            help="Is the carrier method possible with the current order.") #update function reference
    }