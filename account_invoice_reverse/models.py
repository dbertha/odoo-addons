# -*- coding: utf-8 -*-

from openerp import models, SUPERUSER_ID
from openerp.osv import osv, fields
import logging

_logger = logging.getLogger(__name__)


class delivery_carrier(osv.osv) :
    _name = "delivery.carrier"
    _inherit = "delivery.carrier"
    _columns = {
        'journal_id' : fields.many2one('account.journal', string="Purchase Journal",
                help="If is pickup and partner is a company, use this journal for grouped invoices")
    }
    
