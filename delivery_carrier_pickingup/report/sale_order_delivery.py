from openerp.osv import osv
from openerp.tools.translate import _
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone
import pytz
import logging
from openerp import SUPERUSER_ID



_logger = logging.getLogger(__name__)




# #
# # Use period and Journal for selection or resources
# #
# class report_sale_order_delivery(report_sxw.rml_parse):
#     def __init__(self, cr, uid, name, context):
#         super(report_sale_order_delivery, self).__init__(cr, uid, name, context=context)
#         self.localcontext.update()


class SaleOrderDeliveryReport(osv.AbstractModel):
    _name = 'report.delivery_carrier_pickingup.report_saleorder_delivery'


    def render_html(self, cr, uid, ids, data=None, context=None):
        report_obj = self.pool['report']
        report = report_obj._get_report_from_name(cr, uid, 'delivery_carrier_pickingup.report_saleorder_delivery')
        saleorder_obj = self.pool['sale.order']
        tzone = timezone('Europe/Brussels')
        today = date.today()
        period_length = timedelta(days=1)
        period_start = tzone.localize(datetime(today.year, today.month, today.day)).astimezone(pytz.utc)
        period_end = period_start + period_length
        search_domain = [('requested_delivery_datetime_start', '>=', period_start.strftime('%Y-%m-%d %H:%M:%S')), 
                         ('requested_delivery_datetime_start', '<=', period_end.strftime('%Y-%m-%d %H:%M:%S'))]
        saleorder_ids = saleorder_obj.search(cr,SUPERUSER_ID, search_domain, context=context)
        sale_orders = saleorder_obj.browse(cr,SUPERUSER_ID, saleorder_ids, context=context)
        #context.update({'period_start' :period_start,
        #                'perdiod_end' : period_end })
        docargs = {
            'doc_ids': saleorder_ids,
            'doc_model': report.model,
            'docs': sale_orders,
        }
        docargs.update({'period_start' :period_start.astimezone(tzone).strftime('%Y-%m-%d %H:%M:%S'),
                        'period_end' : period_end.astimezone(tzone).strftime('%Y-%m-%d %H:%M:%S') })
        #TODO : FormatLang : rml : deprecated but can be usefull here
        return report_obj.render(cr, uid, ids, 'delivery_carrier_pickingup.report_saleorder_delivery', docargs, context=context)