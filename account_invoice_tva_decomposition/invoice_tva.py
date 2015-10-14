# -*- coding: utf-8 -*-

from openerp.osv import osv
from openerp.tools.translate import _
from datetime import date, datetime, timedelta, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
import pytz
import logging
from openerp import SUPERUSER_ID
from openerp.osv import osv, fields
import calendar


_logger = logging.getLogger(__name__)



class InvoiceReport(osv.AbstractModel):
    
    _name = 'report.account.report_invoice'

    def render_html(self, cr, uid, ids, data=None, context=None):
        if context is None :
            context= {}
        report_obj = self.pool['report']
        report = report_obj._get_report_from_name(cr, uid, 'account.report_invoice')


        docargs = {
            'doc_ids': ids,
            'doc_model': report.model,
            'docs': self.pool.get('account.invoice').browse(cr,uid, ids,context=context),
        }
        
        for invoice in docargs['docs'] :
            taxes = dict()
            
            for line in invoice.invoice_line :
                taxes[line.invoice_line_tax_id.name] = dict()
            for taxe in taxes.iterkeys() :
                taxes[taxe]['name'] = taxe
                taxes[taxe]['total'] = sum([l.invoice_line_tax_id.compute_all(
                    (l.price_unit * (1.0 - (l.discount or 0.0) / 100.0)), l.quantity, l.product_id, invoice.partner_id)['total'] for l in invoice.invoice_line if l.invoice_line_tax_id.name == taxe])
                taxes[taxe]['total_included'] =  sum([l.invoice_line_tax_id.compute_all((l.price_unit * (1.0 - (l.discount or 0.0) / 100.0)),
                                                                                        l.quantity, l.product_id, invoice.partner_id)['total_included'] for l in invoice.invoice_line if l.invoice_line_tax_id.name == taxe] )

                taxes[taxe]['amount'] = sum([l.invoice_line_tax_id.compute_all(
                    (l.price_unit * (1.0 - (l.discount or 0.0) / 100.0)), l.quantity, l.product_id, invoice.partner_id)['taxes'][0]['amount'] for l in invoice.invoice_line if l.invoice_line_tax_id.name == taxe and l.invoice_line_tax_id.compute_all(
                    (l.price_unit * (1.0 - (l.discount or 0.0) / 100.0)), l.quantity, l.product_id, invoice.partner_id)['taxes']])
            docargs.update({'taxes' : taxes})
        _logger.debug("docargs : %s", docargs)
        return report_obj.render(cr, uid, ids, 'account.report_invoice', docargs, context=context)