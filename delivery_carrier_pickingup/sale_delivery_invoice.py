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
from openerp import fields #new api
import calendar


_logger = logging.getLogger(__name__)

class account_invoice(osv.osv):
    _name = 'account.invoice'
    _inherit = 'account.invoice'
    
    def send_grouped_invoices(self, cr,uid,ids, context=None):
        _logger.debug("Will send mail")
        #account_invoice_obj = self.pool.get('account.invoice')
        for invoice_id in ids : #send one by one
            #template = self.env.ref('delivery_carrier_pickingup.email_template_grouped_invoice', False)
            #compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
            #old api way :
            ir_model_data = self.pool.get('ir.model.data')
            template_id = ir_model_data.get_object_reference(cr, uid, 'delivery_carrier_pickingup', 'email_template_grouped_invoice')[1]
            #TODO : handle deletion of template ?
            self.pool.get('email.template').send_mail(cr, uid, template_id, invoice_id, force_send=True, context=context)
            #don't need composer object, we suppose the mail parameters of the template are ok
            


class sale_order(osv.osv):
    _name = "sale.order"
    _inherit = "sale.order"
    
    def cron_grouped_invoices(self,cr,uid,ids=[],length=7, context=None):
        """Grouped invoices : every day which is a multiple of <length> and first day of the month"""
        if context is None : 
            context = {}
        today = date.today()
        yesterday = today - timedelta(days=1) #to be sure the day is over
        last_day_of_month = calendar.monthrange(today.year, today.month)[1]
        if yesterday.day % length == 0 or yesterday.day == last_day_of_month :
            period_end = yesterday
            start_day = (((period_end - timedelta(days=1)).day) / int(length)) * int(length)
            #previous multiple
            period_start =  yesterday - timedelta(yesterday.day - start_day)
            #TODO : check that this period is not already invoiced
            #period_end and period_start
        period_start = datetime(1999,1,1)
        period_end = datetime(2100,2,2)
        context.update({'period_start' : period_start,
                        'period_end' : period_end})
        #TODO : add period in context to retrieve in render_html
        invoice_ids = self.create_delivery_grouped_invoices(cr,uid,ids,period_start,period_end, context=context)
        self.pool.get('account.invoice').send_grouped_invoices(cr,uid, invoice_ids, context=context)
    
    def create_delivery_grouped_invoices(self,cr,uid,ids, period_start, period_end,context=None):
        #TODO : default values for period start et end (end = start + delta)
        """creates invoices for
        sale order sold on eshop for another company (pick-up in
        a independant shop).
        Lighter than multi-companies modules"""
        delivery_carrier_obj = self.pool.get('delivery.carrier')
        delivery_carrier_ids = delivery_carrier_obj.search(cr,SUPERUSER_ID,
                                [('is_pickup', '=', True)], context=context)
        new_invoices = []
        for delivery_in_independant_shop in delivery_carrier_obj.browse(cr, SUPERUSER_ID,delivery_carrier_ids, context=context) :
            if delivery_in_independant_shop.address_partner and delivery_in_independant_shop.address_partner.is_company :
                _logger.debug("Independant shop found")
                new_invoice_id = self.create_delivery_grouped_invoice(cr,uid,delivery_in_independant_shop,period_start, period_end,context=context)
                if new_invoice_id :
                    new_invoices.append(new_invoice_id)
            elif not delivery_in_independant_shop.address_partner :
                _logger.error("Delivery carrier has no related partner")
        _logger.debug("invoices to send : %s", str(new_invoices))
        return new_invoices
        
        
    def create_delivery_grouped_invoice(self,cr,uid,delivery_carrier,period_start,period_end, context=None):
        if context is None :
            context = {}
        if not delivery_carrier.address_partner.email :
            _logger.error("Delivery carrier has no email in his related partner")
        search_domain = [('requested_delivery_datetime_start', '>=', period_start.strftime('%Y-%m-%d %H:%M:%S')), 
                    ('requested_delivery_datetime_start', '<', period_end.strftime('%Y-%m-%d %H:%M:%S')),
                    ('carrier_id', '=', delivery_carrier.id)]
        sale_order_obj = self.pool.get('sale.order')
        order_ids = sale_order_obj.search(cr,SUPERUSER_ID, search_domain, context=context)
        #company = delivery_carrier.address_partner.company_id #TODO : check if correct company_id
        #company of the shop becomes company of the invoice
        customer = delivery_carrier.address_partner
        new_invoice_lines = []
        
        defaults = {
            'create_date':False,
            'invoice_id' : False,
        }
        defaults.update({'partner_id' : customer.id})
        #customer = False
        company = False
        currency = False
        for so in sale_order_obj.browse(cr,SUPERUSER_ID, order_ids, context=context) :
            if not company : 
                company = so.company_id
            if not currency :
                currency = so.pricelist_id.currency_id
            for order_line in so.order_line :
                defaults.update({'origin' : "{}/{}".format(so.name, so.partner_id.name)})
                if not order_line.is_delivery : 
                    _logger.debug("Order line, no delivery")
                    for invoice_line in order_line.invoice_lines :
                        if invoice_line.invoice_id.state != 'cancel'  :
                            _logger.debug("new invoice line")
                            defaults.update({'discount' : invoice_line.product_id.product_tmpl_id.discount or 0 })
                            new_invoice_line_id = self.pool.get('account.invoice.line').copy(cr,uid,invoice_line.id,defaults,context=context)
                            new_invoice_lines.append(new_invoice_line_id)
        if new_invoice_lines :
            if delivery_carrier.journal_id :
                journal = delivery_carrier.journal_id
            else :
                _logger.warning("No purchase journal defined for delivery carrier, searching for one")
                journal_ids = self.pool.get('account.journal').search(cr, SUPERUSER_ID,
                    [('type', '=', 'purchase'), ('company_id', '=', company.id)])
                    #mapping in_invoice - purchase journal
                if not journal_ids:
                    raise osv.except_osv(_('Error!'),
                        _('Please define sales journal for this company: "%s" (id:%d).') % (company.name, company.id))
                
                journal = self.pool.get('account.journal').browse(cr,uid, journal_ids[0], context=context)
            
            #sequential number, no gap : depending of number of entries in journal
            
            invoices_in_journal = self.pool.get('account.invoice').search(cr,SUPERUSER_ID, [('journal_id', '=', journal.id)])
            origin = "{}/{}".format(journal.code, len(invoices_in_journal))
            
            invoice_vals = {
                'name': False,
                'origin': origin,
                'type': 'in_invoice', 
                
                'account_id': customer.property_account_receivable.id,
                'partner_id': customer.id,
                'journal_id': journal.id,
                'invoice_line': [(6, 0, new_invoice_lines)],
                'currency_id': currency.id,
                #'comment': order.note,
                #'payment_term': order.payment_term and order.payment_term.id or False,
                'fiscal_position': customer.property_account_position.id,
                'date_invoice': context.get('date_invoice', date.today().strftime('%Y-%m-%d')),
                'company_id': company.id,
                #'user_id': order.user_id and order.user_id.id or False,
                #'section_id' : order.section_id.id
            }
            context['type'] = invoice_vals['type'] #needed to handle correctly default journal_id
            inv_obj = self.pool.get('account.invoice')
            inv_id = inv_obj.create(cr, uid, invoice_vals, context=context)
            inv_obj.button_compute(cr, uid, [inv_id]) #update check_total
            return inv_id
        return None
    
class GroupedInvoiceReport(osv.AbstractModel):
    
    _name = 'report.delivery_carrier_pickingup.report_group_invoice'


    def render_html(self, cr, uid, ids, data=None, context=None):
        """Add period start and period end from context to args of report template"""
        if context is None :
            context= {}
        report_obj = self.pool['report']
        report = report_obj._get_report_from_name(cr, uid, 'delivery_carrier_pickingup.report_group_invoice')
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
        #TODO : FormatLang : rml : deprecated but can be usefull here
        return report_obj.render(cr, uid, ids, 'delivery_carrier_pickingup.report_group_invoice', docargs, context=context)