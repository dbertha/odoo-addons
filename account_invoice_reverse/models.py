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
    
class InvoiceDiscount(osv.osv) :
    _name = "account.invoice.discount"
    
    def _name_get(self, cr, uid, ids, name, arg, context=None) :
        result = dict.fromkeys(ids, False)
        for discount in self.browse(cr, uid, ids, context=context) :
            result[discount.id] = "{0}%".format(discount.percentage)
        return result
    
    _columns = {
        'percentage' : fields.integer(string='Discount percentage', 
            help='Discount to apply on reverse invoice. Between 0 and 100', default=0, required=True),
        'name' : fields.function(_name_get,type='char', string='Name')
    }
    
    def _check_percentage(self, cr, uid, ids, context = None) :
        discount = self.browse(cr, uid, ids, context=context)
        return 0 <= discount.percentage <= 100
    
    _constraints = [
        (_check_percentage, 'The percentage should be between 0 and 100', ['percentage'])]
    
class ProductTemplate(osv.osv) :
    _name = "product.template"
    _inherit = "product.template"
    _columns = {
        'discount_id' : fields.many2one('account.invoice.discount', string="Reverse Invoice Discount",
                help="Discount to apply to invoice lines with that product when reverse grouped invoiced is generated")
    }
    
    def force_default(self, cr, uid, ids = [], discount_id=0, context=None) :
        """Quick solution to avoid encoding the same discount manually for each product
        User should be admin"""
        assert uid == SUPERUSER_ID, "User to force discount value should be the administrator"
        product_ids = self.search(cr, uid, [], discount_id, context=context)
        _logger.debug("Dicount id force default : %d", discount_id)
        self.write(cr, uid, product_ids, {'discount_id' : discount_id}, context=context)
        
