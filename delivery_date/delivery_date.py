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
    
    def get_min_date(self,cr,uid, ids, context) :
        """Compute rules for delivery based on the sale order.
        Possible improvement : use strategy pattern and delegate computation
        to those classes
        Assert : only one ID"""
        #date_today = date.today()
        _logger.debug("Original get_min_date")
        tzone = timezone('Europe/Brussels')
        now = pytz.utc.localize(datetime.now()).astimezone(tzone)
        #now = now.replace(hour=now.hour + 1,minute=59)
        delta = timedelta(hours=1)
        now = now.replace(minute=59) + delta 
        return [now.year, now.month, now.day, now.hour, now.minute]
        
    def get_max_date(self,cr,uid, ids, context) :
        """Compute rules for delivery based on the sale order.
        Possible improvement : use strategy pattern and delegate computation
        to those classes. Linked to a set of categories of products
        Assert : only one ID"""
        #date_today = date.today()
        tzone = timezone('Europe/Brussels')
        now = pytz.utc.localize(datetime.now()).astimezone(tzone)
        return [2100,1,1]
    
    def get_forbidden_days(self,cr,uid, ids, context) :
        """Compute forbidden days for delivery
        Assert : only one ID"""
        return []  
    
    def check_date(self, cr,uid, ids, datetime_start,context) :
        """check if date is between min and max acceptable date for delivery
        and not in a forbidden day"""
        tzone = timezone('Europe/Brussels')
        now = pytz.utc.localize(datetime.now()).astimezone(tzone)
        min_datetime = tzone.localize(datetime(*self.get_min_date(cr, uid, ids, context)))
        max_datetime_param = self.get_max_date(cr, uid, ids, context) or [2100,1,1] #a date far away
        _logger.debug("max param : %s", str(max_datetime_param))
        max_datetime = tzone.localize(datetime(*max_datetime_param))
        forbidden_days = self.get_forbidden_days(cr, uid, ids, context)
        _logger.debug("form validate datetime_start : %s | min : %s | max : %s", 
            datetime_start.strftime("%d/%m/%Y %H:%M"),min_datetime.strftime("%d/%m/%Y %H:%M"), max_datetime.strftime("%d/%m/%Y %H:%M") )
        if ((now + timedelta(hours=1)) > datetime_start) : #sould be enough in future
            _logger.debug("form validate : not in future")
            return False
        if(datetime_start.minute != 0) :
            _logger.debug("form validate : minutes not 0")
            return False
        if((datetime_start.hour < 10) or (datetime_start.hour > 18)) :
            _logger.debug("form validate : hour not in correct interval")
            return False
        if(not(min_datetime <= datetime_start <= max_datetime)) :
            _logger.debug("form validate : day not in correct interval")
            return False 
        if(datetime_start.weekday() in forbidden_days) :
            _logger.debug("form validate : forbidden day")
            return False
        _logger.debug("form validate : date ok")
        return True