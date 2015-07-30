# -*- coding: utf-8 -*-

#sur base de res partner ou sur base de delivery_carrier ?
#reprendre les références des SOs et du client : impossible dans la structure de base...
#on peut créer un pdf mais pas à partir d'une facture car celle-ci aura perdu les références
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


class sale_order(osv.osv):
    _name = "sale.order"
    _inherit = "sale.order"
    
    def _get_sale_orders_with_group(self, cr, uid, ids, group_by,group_id, period_start, period_end, context=None) :
        """Return order_ids and some invoice values depending of the grouping parameter"""
        if group_by == 'partner_id' : #TODO : enumerate ?
            search_domain = [('requested_delivery_datetime_start', '>=', period_start.strftime('%Y-%m-%d %H:%M:%S')), 
                    ('requested_delivery_datetime_start', '<', period_end.strftime('%Y-%m-%d %H:%M:%S')),
                    ('partner_id', '=', group_id)]
            sale_order_obj = self.pool.get('sale.order')
            order_ids = sale_order_obj.search(cr,SUPERUSER_ID, search_domain, context=context)
            invoice_vals = {'partner_id' : group_id}
            return order_ids, invoice_vals
        return [], {}
     
    def create_grouped_invoice(self,cr,uid,ids,group_by,group_id,period_start,period_end, invoice_delivery=True,apply_discount=False, service_to_add=False, context=None):
        """This method can be used to generate a new invoice from a set of order,
        with several parameters :
        @param group_by: string of the attribute to consider, 
        the grouping method can determine most of the invoice values like its partner or its journal
        @param group_id: id of the record to match the attribute from group_by
        @param period_start: datetime object, lower bound of interval for the delivery date of sale orders
        @param period_end: datetime object, upper bound of interval for the delivery date of sale orders
        @param invoice_delivery: boolean indicating of delivery lines should be invoiced too
        @param apply_discount: boolean indicating if a discount should be applied. Not used in this module
        @param service_to_add: if not False, should be a product.product record representing a service to invoice with the sale orders
        """
        if context is None :
            context = {}
            
        #hook point
        sale_order_ids, invoice_vals = self._get_sale_orders_with_group(cr, uid, ids, group_by,group_id, period_start, period_end, context=context)
        #rem : can pass invoice_vals through context ?
        inv_line_values = {'create_date' : False,
                           'invoice_id' : False,
            }
        all_invoice_lines = []
        _logger.debug("Sale order to invoice : %s", sale_order_ids)
        for sale_order in self.browse(cr, uid, sale_order_ids, context=context) :
            if not invoice_vals.get('company_id') :
                invoice_vals['company_id'] = sale_order.company_id.id
            if not invoice_vals.get('currency_id') :
                invoice_vals['currency_id'] = sale_order.pricelist_id.currency_id.id
            if not invoice_vals.get('partner_id') :
                invoice_vals['partner_id'] = sale_order.partner_id.id
                
            line_ids = [line.id for line in sale_order.order_line if invoice_delivery or not line.is_delivery ]
            _logger.debug("Line from SO to invoice : %s", line_ids)
            inv_line_ids = self.pool.get('sale.order.line').invoice_line_create(cr, uid, line_ids, context=context)
            _logger.debug("created Invoice lines : %s", inv_line_ids)
            inv_line_values.update({'partner_id' : invoice_vals.get('partner_id'),
                               'origin' : "{}/{}".format(sale_order.name, sale_order.partner_id.name)})
            inv_line_obj = self.pool.get('account.invoice.line')
            if not apply_discount :
                #write all in once
                inv_line_obj.write(cr, uid, inv_line_ids, inv_line_values, context=context)
            else :
                for invoice_line in inv_line_obj.browse(cr, uid, inv_line_ids, context=context) :
                    inv_line_values.update({'discount' : invoice_line.product_id.product_tmpl_id.discount_id 
                                            and invoice_line.product_id.product_tmpl_id.discount_id.percentage or 0})
                    inv_line_obj.write(cr, uid, invoice_line.id, inv_line_values, context=context)
            all_invoice_lines += inv_line_ids
        if service_to_add :
            inv_line_values.update({'name': service_to_add.name,
                                    'discount' : 0,
                                    'origin' : "service for grouped invoice",
                                    'account_id' : service_to_add.property_account_income.id or service_to_add.categ_id.property_account_income_categ.id,
                                    'quantity' : 1,
                                    'price_unit': round(service_to_add.price,
                        self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Price')),
                                    'product_id' : service_to_add.id,
                                    'invoice_line_tax_id': [(6, 0, [x.id for x in service_to_add.taxes_id])],
                                    'uos_id': service_to_add.uom_id.id})
            service_invoice_line = inv_line_obj.create(cr, uid, inv_line_values, context=context)
            all_invoice_lines += [service_invoice_line]
            
        if not invoice_vals.get('journal_id') :
            journal_ids = self.pool.get('account.journal').search(cr, SUPERUSER_ID,
                [('type', '=', 'sale'), ('company_id', '=', invoice_vals.get('company_id'))])
            if not journal_ids:
                company = self.pool.get('res.company').browse(cr, SUPERUSER_ID, invoice_vals.get('company_id'), context=context)
                raise osv.except_osv(_('Error!'),
                    _('Please define sales journal for this company: "%s" (id:%d).') % (company.name, company.id))
                 
            invoice_vals['journal_id'] = journal_ids[0]
        if not invoice_vals.get('origin') :
            invoice_vals['origin'] = False
        if not invoice_vals.get('type') :
            invoice_vals['type'] = "out_invoice"
        if not invoice_vals.get('date_invoice') :
            invoice_vals['date_invoice'] = context.get('date_invoice', date.today().strftime('%Y-%m-%d'))
        partner = self.pool.get('res.partner').browse(cr, uid, invoice_vals.get('partner_id'), context=context)
        if not invoice_vals.get('fiscal_position') :
            invoice_vals['fiscal_position'] = partner.property_account_position.id
        if not invoice_vals.get('account_id') :
            invoice_vals['account_id'] = partner.property_account_receivable.id
        invoice_vals['invoice_line'] = [(6, 0, all_invoice_lines)]

        _logger.debug("Grouped Invoice values : %s", invoice_vals)
        if all_invoice_lines :
            context['type'] = invoice_vals['type'] #needed to handle correctly default journal_id
            inv_obj = self.pool.get('account.invoice')
            inv_id = inv_obj.create(cr, uid, invoice_vals, context=context)
            inv_obj.button_compute(cr, uid, [inv_id]) #update check_total
            #link order to invoice
            if isinstance(sale_order_ids, (int, long)) :
                sale_order_ids = [sale_order_ids]
            for order_id in sale_order_ids :
                cr.execute('insert into sale_order_invoice_rel (order_id,invoice_id) values (%s,%s)', (order_id, inv_id))
            self.invalidate_cache(cr, uid, ['invoice_ids'], sale_order_ids, context=context)
            #self.write(cr, uid, sale_order_ids, {'invoice_ids' : [(6, 0, inv_id)]}, context=context)
            return inv_id
        return None
    
    
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
    
    def force_default_discount(self, cr, uid, ids = [], discount_id=0, context=None) :
        """Quick solution to avoid encoding the same discount manually for each product
        User should be admin"""
        assert uid == SUPERUSER_ID, "User to force discount value should be the administrator"
        product_ids = self.search(cr, uid, [], discount_id, context=context)
        _logger.debug("Dicount id force default : %d", discount_id)
        self.write(cr, uid, product_ids, {'discount_id' : discount_id}, context=context)
        
    def force_default_taxes(self, cr, uid, ids = [], taxes_ids=[1], context=None) :
        """Quick solution to avoid encoding the same taxes manually for each product
        User should be admin"""
        assert uid == SUPERUSER_ID, "User to force discount value should be the administrator"
        product_ids = self.search(cr, uid, [], context=context)
        _logger.debug("Taxes ids force default : %d", taxes_ids)
        self.write(cr, uid, product_ids, {'taxes_id' : [(6,0,taxes_ids)]}, context=context)
        
class GroupedInvoiceReport(osv.AbstractModel):
    
    _name = 'report.account_grouped_invoice.report_group_invoice'

    def render_html(self, cr, uid, ids, data=None, context=None):
        """Add period start and period end from context to args of report template"""
        if context is None :
            context= {}
        report_obj = self.pool['report']
        report = report_obj._get_report_from_name(cr, uid, 'account_grouped_invoice.report_group_invoice')
        tzone = timezone('Europe/Brussels')

        docargs = {
            'doc_ids': ids,
            'doc_model': report.model,
            'docs': self.pool.get('account.invoice').browse(cr,uid, ids,context=context),
        }
        if context.get('period_start', False) and context.get('period_end', False) :
            _logger.debug("Add period to template args")
            docargs.update({'period_start' :context.get('period_start').strftime('%d/%m/%Y'),
                        'period_end' : context.get('period_end').strftime('%d/%m/%Y')})
        if context.get('reverse', False) :
            docargs.update({'reverse' : context.get('reverse')})
        else :
            _logger.debug("Test if in_invoice")
            for invoice in docargs['docs'] :
                if invoice.type == "in_invoice" :
                    docargs.update({'reverse' : True})
        #TODO : FormatLang : rml : deprecated but can be usefull here
        return report_obj.render(cr, uid, ids, 'account_grouped_invoice.report_group_invoice', docargs, context=context)