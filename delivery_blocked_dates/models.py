# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp
import logging
from openerp import SUPERUSER_ID

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import pytz
from pytz import timezone
from __builtin__ import str
_logger = logging.getLogger(__name__)


# class DeliveryCarrier(osv.osv) :
#     _name = "delivery.carrier"
#     _inherit = "delivery.carrier"
    
#     _columns = {
#         'blocked_date_ids' : fields.many2many('delivery.blocked_date',
#             'delivery_carrier_blocked_dates_rel','carrier_id','blocked_date_id', string='Blocked Dates', 
#             help='Specific days when the delivery carrier is not available. Warning : they can be specific to a delivery condition')
#     }

# class DeliveryCondition(osv.osv) :
#     _name = "delivery.condition"
#     _inherit = "delivery.condition"
    
#     _columns = {
#         'blocked_date_ids' : fields.many2many('delivery.blocked_date',
#             'delivery_condition_blocked_dates_rel','condition_id','blocked_date_id', string='Blocked Dates', 
#             help='Specific days when the delivery condition is not available. Warning : they can be specific to a delivery carrier')
#     }
    

    
class DeliveryBlockedDate(osv.osv) :
    _name = "delivery.blocked_date"
    _order = 'year asc, month asc, day asc'
    
    def _name_get(self, cr, uid, ids, name, arg, context=None) :
        result = dict.fromkeys(ids, False)
        for blocked_date in self.browse(cr, SUPERUSER_ID, ids, context=context) :
            computed_name = "{0}/{1}/{2} ".format(blocked_date.day, blocked_date.month, blocked_date.year)
            computed_name += blocked_date.carrier_id and blocked_date.carrier_id.name or ''
            computed_name += " "
            computed_name += blocked_date.condition_id and blocked_date.condition_id.name or ''
            result[blocked_date.id] = computed_name
        return result
    
    _columns = {
        'name' : fields.function(_name_get, type='char', string='Name'),
        'year' : fields.selection(
                [(2016, '2016'), (2017, '2017'), (2018, '2018')], 
                string="Year", required=True
                ),
        'month' : fields.selection(
                [(1,"01"), (2,"02"), (3,"03"), (4,"04"),
                 (5,"05"), (6,"06"), (7,"07"), (8,"08"),
                 (9, '09'), (10, '10'), (11, '11'), (12, '12')], 
                 string="Month", required=True),
        'day' : fields.selection(
                [(1,"01"), (2,"02"), (3,"03"), (4,"04"),
                 (5,"05"), (6,"06"), (7,"07"), (8,"08"),
                 (9, '09'), (10, '10'), (11, '11'), (12, '12'),
                 (13, '13'), (14, '14'), (15, '15'), (16, '16'),
                 (17, '17'), (18, '18'), (19, '19'), (20, '20'), 
                 (21, '21'), (22, '22'), (23, '23'), (24, '24'), 
                 (25, '25'), (26, '26'), (27, '27'), (28, '28'),
                 (29, '29'), (30, '30'), (31, '31')], 
                 string="Day", required=True),
        'carrier_id' : fields.many2one("delivery.carrier", 
            string="Delivery Carrier"),
        'condition_id' : fields.many2one("delivery.condition", 
            string="Delivery Condition")
    }

    
class SaleOrder(osv.osv):
    _name = "sale.order"
    _inherit = "sale.order"

    def get_forbidden_time_intervals(self,cr,uid, order,  min_date=None, max_date=None, context=None) :
        res = super(SaleOrder,self).get_forbidden_time_intervals(cr, uid, order, min_date=min_date, max_date=max_date, context=context) 
        delivery_carrier = order.carrier_id
        delivery_condition = order.delivery_condition
        #TODO : the logic should be in blocked_date class
        search_domain = ['|', '|','|', '&', ['carrier_id', '=', delivery_carrier.id], ['condition_id', '=', False],
                        #delivery carrier specific
                        '&', ['carrier_id', '=', False], ['condition_id', '=', delivery_condition.id],
                        #delivery condition specific
                        '&', ['carrier_id', '=', delivery_carrier.id], ['condition_id', '=', delivery_condition.id],
                        #delivery carrier and delivery condition specific
                        '&', ['carrier_id', '=', False], ['condition_id', '=', False],
                        #for any delivery carrier or condition
                        ]
        forbidden_days_ids = self.pool['delivery.blocked_date'].search(cr, SUPERUSER_ID, search_domain, context=context)
        tzone = timezone('Europe/Brussels') #TODO : timezone usefull here ?
        _logger.debug(forbidden_days_ids)
        for forbidden_day in self.pool['delivery.blocked_date'].browse(cr, SUPERUSER_ID, forbidden_days_ids) :
            min_datetime = tzone.localize(datetime(forbidden_day.year, forbidden_day.month, forbidden_day.day, 0, 0))
            _logger.debug(min_datetime)
            today = date.today()
            should_be_add = min_datetime > tzone.localize(datetime(today.year, today.month, today.day))  #in the future
            if min_date : should_be_add = should_be_add and tzone.localize(datetime(*min_date)) < min_datetime
            if max_date : should_be_add = should_be_add and tzone.localize(datetime(*max_date)) > min_datetime
            #TODO : check if date not already in blocked intervals
            if should_be_add :
                start_of_interval = [min_datetime.year, min_datetime.month, min_datetime.day, 0, 0]
                end_of_interval = [min_datetime.year, min_datetime.month, min_datetime.day, 23, 59]
                _logger.debug(start_of_interval)
                _logger.debug(end_of_interval)
                res.append([start_of_interval, end_of_interval])
        return res;
    