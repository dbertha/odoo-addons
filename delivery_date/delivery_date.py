# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import pytz

import openerp
from openerp import SUPERUSER_ID
from openerp.addons.web.http import request
from openerp.osv import fields
from openerp import models
from pytz import timezone
import logging

_logger = logging.getLogger(__name__)
class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = 'sale.order'
    _columns = {
        #'requested_delivery_date' : fields.date(string='Requested Delivery Date', help="Date requested by the customer for the delivery."),
        'requested_delivery_datetime_start' : fields.datetime(string='Requested Delivery Interval Beginning',
            help='The begin of the time interval requested for the delivery'),
        'requested_delivery_datetime_end' : fields.datetime(string='Requested Delivery Interval Ending',
            help='The end of the time interval requested for the delivery')
    }
    
    def get_forbidden_time_intervals(self,cr,uid, ids, min_date=None, max_date=None, context=None) :
        """Compute rules for delivery based on the sale order.
        Bounds included.
        Assert : only one ID"""
        return []
    
    def get_datetime_format(self, cr, uid, order, context=None) :
        """Can be overloaded easily"""
        return 'ddd DD/MM/YYYY HH:mm' # %a %d/%m/%Y %H:%m
    
    def get_min_date(self,cr,uid, order, forbidden_days=None, context=None) :
        """Compute rules for delivery based on the sale order.
        Possible improvement : use strategy pattern and delegate computation
        to those classes"""
        #date_today = date.today()
        _logger.debug("Original get_min_date")
        tzone = timezone('Europe/Brussels')
        now = pytz.utc.localize(datetime.now()).astimezone(tzone)
        #now = now.replace(hour=now.hour + 1,minute=59)
        delta = timedelta(hours=1)
        now = now.replace(minute=59) + delta 
        return [now.year, now.month, now.day, now.hour, now.minute]
        
    def get_max_date(self,cr,uid, order, min_date=None, forbidden_days=None, context=None) :
        """Compute rules for delivery based on the sale order.
        Can be overloaded to specify rules relative to delivery carriers, products in cart,...
        Assert : only one ID
        Default : 30 days from now"""
        #date_today = date.today()
        min_datetime = timezone('Europe/Brussels').localize(datetime(*min_date))
        #now = pytz.utc.localize(datetime.now()).astimezone(tzone)
        min_datetime += timedelta(days=30)
        return [min_datetime.year, min_datetime.month, min_datetime.day, min_datetime.hour, min_datetime.minute]
    
    def get_forbidden_days(self,cr,uid, order, context=None) :
        """Compute forbidden days for delivery
        Assert : only one ID"""
        return []  
    
    def check_date(self, cr,uid, ids, datetime_start,context=None) :
        """check if date is between min and max acceptable date for delivery
        and not in a forbidden day"""
        tzone = timezone('Europe/Brussels')
        now = pytz.utc.localize(datetime.now()).astimezone(tzone)
        order = self.browse(cr, uid, ids, context=context)
        forbidden_days = self.get_forbidden_days(cr, uid, order, context=context)
        
        min_datetime_list = self.get_min_date(cr, uid, order, forbidden_days=forbidden_days, context=context)
        min_datetime = tzone.localize(datetime(*min_datetime_list))
        max_datetime_param = self.get_max_date(cr, uid, order, min_date=min_datetime_list, forbidden_days=forbidden_days, context=context) or [2100,1,1] #a date far away
        _logger.debug("max param : %s", str(max_datetime_param))
        max_datetime = tzone.localize(datetime(*max_datetime_param))
        _logger.debug("form validate datetime_start : %s | min : %s | max : %s", 
            datetime_start.strftime("%d/%m/%Y %H:%M"),min_datetime.strftime("%d/%m/%Y %H:%M"), max_datetime.strftime("%d/%m/%Y %H:%M") )
        if ((now + timedelta(hours=1)) > datetime_start) : #sould be enough in future
            _logger.debug("form validate : not in future")
            return False
        if(datetime_start.minute != 0) :
            _logger.debug("form validate : minutes not 0")
            return False
        if((datetime_start.hour < 10) or (datetime_start.hour > 18)) : #TODO : use intervals instead
            _logger.debug("form validate : hour not in correct interval")
            return False
        if(not(min_datetime <= datetime_start <= max_datetime)) :
            _logger.debug("form validate : day not in correct interval")
            return False 
        if(datetime_start.weekday() in forbidden_days) :
            _logger.debug("form validate : forbidden day")
            return False
        forbidden_intervals = self.get_forbidden_time_intervals(cr, uid, order, min_date=min_datetime_list, max_date=max_datetime_param, context=context)
        forbidden_datetimes_intervals = [ [tzone.localize(datetime(*x)) for x in interval ] for interval in forbidden_intervals]
        for interval in forbidden_datetimes_intervals :
            if interval[0] < datetime_start < interval[1] :
                _logger.debug("form validate : forbidden interval")
                return False
        _logger.debug("form validate : date ok")
        return True