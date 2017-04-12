# -*- coding: utf-8 -*-

import openerp.addons.decimal_precision as dp
import logging
from openerp import SUPERUSER_ID
from openerp import api, fields, models, _

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import pytz
from pytz import timezone
from __builtin__ import str
_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model) :
    _name = "delivery.carrier"
    _inherit = "delivery.carrier"
    

    delivery_period_ids = fields.Many2many('delivery.period',
            'delivery_carrier_period_rel','carrier_id','period_id', string='Periods', 
            help='Periods of the week where this delivery method can be requested. No period is considered as always (other constraints are still valid)')
    
    #TODO : no overlap
    

    
class DeliveryPeriod(models.Model) :
    _name = "delivery.period"
    #TODO : handle all day
    _rec_name = 'name'
    _order = 'day_of_week asc, start_hour asc'
    
    @api.multi
    @api.depends('name','day_of_week', 'start_hour', 'start_min', 'end_hour', 'end_min')
    def name_get(self) :
        days = ['','Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        result = []
        for period in self :
            name = "{0} {1:0>2d}h{2:0>2d} - {3:0>2d}h{4:0>2d}".format(
                    days[period.day_of_week][0:3], period.start_hour, 0 if period.start_min == 1 else period.start_min, period.end_hour, 0 if period.end_min == 1 else period.end_min)
            period.name = name
            result.append((period.id, name))
        return result
    

    name = fields.Char(compute="name_get")
    day_of_week = fields.Selection(
                [(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), 
                 (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')], #1-7 because no selection == 0
                string="Day of the week", required=True
                )
    start_hour = fields.Selection(
                [(1,"01"), (2,"02"), (3,"03"), (4,"04"),
                 (5,"05"), (6,"06"), (7,"07"), (8,"08"),
                 (9, '09'), (10, '10'), (11, '11'), (12, '12'),
                 (13, '13'), (14, '14'), (15, '15'), (16, '16'),
                 (17, '17'), (18, '18'), (19, '19'), (20, '20'), 
                 (21, '21'), (22, '22'), (23, '23')], string="Hour of start time", default=1, required=True)
    start_min = fields.Selection(
                [(01,"00"), (15,"15"), (30,"30"), (45,"45")], string="Minutes of start time", default=1, required=True)
    end_hour = fields.Selection(
                [(1,"01"), (2,"02"), (3,"03"), (4,"04"),
                 (5,"05"), (6,"06"), (7,"07"), (8,"08"),
                 (9, '09'), (10, '10'), (11, '11'), (12, '12'),
                 (13, '13'), (14, '14'), (15, '15'), (16, '16'),
                 (17, '17'), (18, '18'), (19, '19'), (20, '20'), 
                 (21, '21'), (22, '22'), (23, '23')], string="Hour of end time", default=23, required=True)
    end_min = fields.Selection(
                [(01,"00"), (15,"15"), (30,"30"), (45,"45")], string="Minutes of end time", default=1, required=True)
    
    @api.one
    @api.constrains('end_hour', 'start_hour', 'end_min', 'start_min')
    def _check_dates(self) :
        period = self
        if not (period.end_hour > period.start_hour) :
            
            if period.end_hour == period.start_hour :
                if period.end_min <= period.start_min :
                    raise ValidationError(_('The end of the period should be after the start.'))
            else : 
                raise ValidationError(_('The end of the period should be after the start.'))
    

class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = "sale.order"
    

    def get_forbidden_time_intervals(self,min_date=None, max_date=None) :
        intervals = super(SaleOrder,self).get_forbidden_time_intervals(min_date=min_date, max_date=max_date) 
        if min_date and max_date :
            #nothing to compute if the is not an interval to check
            #TODO: can use forbidden_days also
            #order = self.browse(cr, SUPERUSER_ID, order_id, context)
            delivery_carrier = self.carrier_id
            allowed_daytimes = {}
            if delivery_carrier and delivery_carrier.delivery_period_ids :
                for period in delivery_carrier.delivery_period_ids :
                    #for each day, a list of list of tuples
                    allowed_daytimes[period.day_of_week] = allowed_daytimes.get(period.day_of_week, []) + \
                        [[(period.start_hour, (0 if period.start_min == 1 else period.start_min)), (period.end_hour, (0 if period.end_min == 1 else period.end_min))]]
            if allowed_daytimes :
                _logger.debug("Allowed daytimes : %s", str(allowed_daytimes))
                tzone = timezone('Europe/Brussels')
                min_datetime = tzone.localize(datetime(*min_date))
                max_datetime = tzone.localize(datetime(*max_date))
                assert max_datetime >= min_datetime
                current_day = min_datetime
                one_day_delta = timedelta(days = 1)
                _logger.debug("min date %s max date %s", str(min_datetime), str(max_datetime))
                while(current_day < max_datetime) :
                    _logger.debug("current_day %s", str(current_day))
                    if current_day.isoweekday() in allowed_daytimes.keys() :
                        #TODO : end of interval allowed : ok or not ?
                        start_of_interval = [current_day.year, current_day.month, current_day.day, 0, 0]
                        
                        for daily_interval in allowed_daytimes[current_day.isoweekday()] :
                            #supposed ordered and no overlap
                            
                            end_of_interval = [current_day.year, current_day.month, current_day.day, daily_interval[0][0], daily_interval[0][1]]
                            _logger.debug("current_day %s, min_datetime %s, tomorrow %s", str(current_day.date()), str(min_datetime.date()), str((date.today() + timedelta(days=1))))
                            if current_day.date() == date.today() \
                                    or (current_day.date() == min_datetime.date() \
                                    and current_day.date() == (date.today() + timedelta(days=1))) : 
                                end_of_interval[3] += 1 #disable first hour of opening if min_date is today or tomorrow, because order will not be ready
                                _logger.debug("end of interval : %s", str(end_of_interval))
                            intervals.append([start_of_interval, end_of_interval])
                            start_of_interval = end_of_interval[0:3] + [daily_interval[1][0], daily_interval[1][1]]
                        intervals.append([start_of_interval, [current_day.year, current_day.month, current_day.day, 23, 59]])
                            
                            
                    else :
                        #all day should be forbidden
                        intervals.append([[current_day.year, current_day.month, current_day.day, 0, 0], [current_day.year, current_day.month, current_day.day, 23, 59]])
                    current_day += one_day_delta
        #intervals.append([[date.today().year+1,1,1,0,0],[date.today().year+1,1,1,23,59]]) #first of january always closed
        return intervals