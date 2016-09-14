# -*- coding: utf-8 -*-


from cStringIO import StringIO

from openerp.report.report_sxw import report_sxw
from openerp.api import Environment

import logging
_logger = logging.getLogger(__name__)

from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
from datetime import date, time, datetime

class InvoiceToTopaccountXlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, invoices):
        #TODO : wizard for exercice code
        bold = workbook.add_format({'bold': True})
        report_name = "invoices_from_odoo"
        sheet = workbook.add_worksheet(report_name[:31])
        # Start from the first cell. Rows and columns are zero indexed.
        row = 0
        col = 0
        col_nb_map = {
            'document_type' : 0,
            'journal' : 1,
            'exercice' : 2,
            'period' : 3,
            'doc_num' : 4,
            'bis_nb' : 5,
            'num_line' : 6,
            'document_date' : 7,
            'client_num' : 23,
            'account_num' : 27,
            'line_total_vat_included' : 28,
            'line_total_vat_only' : 29,
            'document_vat_code' : 33,
        }
        doc_type_map = {
            'out_invoice' : 1,
            'out_refund' : 2,
            'in_invoie' : 3,
            'in_refund' : 4
        }
#         tax_map = {
#             0 : 0,
#             6 : 1,
#             12 : 2,
#             21 : 3
#         }
        document_type = 1 #"Facture de vente",2 crédit de vente, 3 facture achat, 4 crédit achat
        journal = exercice = period = doc_num = bis_nb = num_line = document_date = client_num = account_num = total_vat_included = total_vat_only = document_vat_code = None
        for invoice in invoices:
            document_type = doc_type_map[invoice.type] # == 'out_invoice') and 1 or 2
            #TODO : parse invoice.number : last 4digits
            # invoice.date_invoice format : "2016-06-18", should be dd/mm/yyyy
            
            journal = 'TL' if invoice.partner_id.x_b2b else 'OL'
            
            invoice_date_object = date.strptime('%Y-%m-%d')
            document_date = invoice_date_object.strftime('%d/%m/%Y')
            exercice = (invoice_date_object.month - 9 ) % 12
            #period
            doc_num = invoice.number[-4:] #last four digits
            #num_bis : 
              #10 = date, devise, unité
              #11 :
                #line 0 : compte client, total_included, total_tva
                #line 1 : montant hors tva sans livraison (total_tva = 0)
                #line 2 : montant hors tva livraison (total_tva = 0)
              #12, line 0 : décomposition TVA
              #15 : 
            for tax in invoice.tax_line_ids :
                #tax.base
                #tva only : "tax.amount
                #total included : "(tax.base + tax.amount)"
            #write the line
                for var_name, col in col_nb_map :
                    sheet.write(row, col, eval(var_name))
            
            


InvoiceToTopaccountXlsx('report.account.invoice.xlsx',
            'account.invoice')