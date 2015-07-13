# -*- coding: utf-8 -*-

from openerp import models
from openerp.osv import osv, fields
import logging

_logger = logging.getLogger(__name__)


class ResPartner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _columns = {
        'accept_invoice' : fields.boolean(
                    help="Mail address will be used in invoice email template or not according to this field",
                    string="Accept Invoice", default=1)
    }
    