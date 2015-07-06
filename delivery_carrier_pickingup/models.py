# -*- coding: utf-8 -*-

from openerp import models
from openerp.osv import osv, fields
import logging

_logger = logging.getLogger(__name__)


class delivery_carrier(osv.osv):
    _name = "delivery.carrier"
    _inherit = "delivery.carrier"
    _columns = {
        'is_pickup' : fields.boolean(string='Is a shop pick-up', 
            help='if activated, the address of delivery_method will be used as shipping address'),
        'address_partner' : fields.many2one('res.partner', string="Address", 
            help="Address to use as shipping address."+ 
            "If no pickup, this field can still be used to store an email address to be notified when this delivery carrier is used"),
        'journal_id' : fields.many2one('account.journal', string="Purchase Journal",
                help="If is pickup and partner is a company, use this journal for grouped invoices")
    }
