# -*- coding: utf-8 -*-
import werkzeug

from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug
import openerp.addons.website_sale.controllers.main
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone
import pytz
import logging

_logger = logging.getLogger(__name__)
class website_sale(openerp.addons.website_sale.controllers.main.website_sale):

    def checkout_values(self, data=None):
        """Overload to add delivery date parsing"""
        _logger.debug("DATA dict when checkout_values of delivery_date module : %s", data)
        values = super(website_sale, self).checkout_values(data)
        values['checkout'].update(self._parse_delivery_date(data))
        #_logger.debug("checkout value end, checkout delivery datetime start : %s", values['checkout']['delivery_datetime_start'])
        return values
    
    def convert_format(self, date_format) :
        conversion_dict = {'ddd' : '%a',
         'DD' : '%d',
         'MM' : '%m',
         'YYYY' : '%Y',
         'HH' : '%H',
         'mm' : '%M',
         }
        for original,replace in conversion_dict.iteritems() :
            date_format = date_format.replace(original, replace)
        return date_format
        
    def _parse_delivery_date(self, data):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        if data and data.get('delivery_date') :
            
            tzone = timezone('Europe/Brussels')
            delivery_interval_time = timedelta(minutes=30)
            _logger.debug("checkout value delivery_date : %s", data.get('delivery_date'))
            order = request.website.sale_get_order(force_create=1, context=context)
            order_obj = registry.get('sale.order')
            datetime_format = self.convert_format(order.get_datetime_format())
            _logger.debug("format : %s", datetime_format)
            try :
                datetime_start = datetime.strptime(data.get('delivery_date'), datetime_format)
                datetime_start = tzone.localize(datetime_start).astimezone(pytz.utc)
                _logger.debug("delivery date from format : %s", datetime_start)
            except :
                _logger.error("Incorrect date %s for format : %s", data.get('delivery_date'), datetime_format)
                return {}

            _logger.debug("checkout value end, checkout delivery datetime start : %s", datetime_start)

            return {'requested_date' : datetime_start,
                 }
        _logger.debug("/!\\  no delivery_date /!\\ ")
        return {}

    def checkout_form_save(self, checkout):
        """overload to store delivery date"""
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry

        order = request.website.sale_get_order(context=context)

        
        super(website_sale, self).checkout_form_save(checkout)

        #need to add delivery date
        _logger.debug("checkout form save, before write : checkout delivery date time start : %s", checkout.get('requested_date'))
        order.requested_date = checkout.get('requested_date')
        

    def check_date_validity(self, date_time):
        tzone = timezone('Europe/Brussels')
        datetime_start = date_time.astimezone(tzone)        
        uid = request.uid
        context = request.context
        cr = request.cr
        order = request.website.sale_get_order(context=context)
        return order.check_date(datetime_start)
        
    def checkout_form_validate(self, data):
        _logger.debug("Validating form")
        error, error_messages = super(website_sale, self).checkout_form_validate(data)
        if not data.get("requested_date") : 
            _logger.debug("form validate : delivery date missing")
            error['delivery_date'] = 'missing'
            error_messages.append('Delivery date is missing')
        elif not self.check_date_validity(data.get('requested_date')) :
            _logger.debug("form validate : delivery date not correct")
            error['delivery_date'] = 'notAcceptable'
            error_messages.append('Delivery date is out of the allowed range')
        _logger.debug("form validate : error : %s", str(error))
        return error, error_messages
    
    @http.route('/shop/checkout/get_dates', type='json', auth="public")
    def get_dates(self):
        uid = request.uid
        context = request.context
        cr = request.cr
        sale_order_obj = request.registry['sale.order']
        order_id = request.session.get('sale_order_id')
        order = sale_order_obj.browse(cr, uid,order_id, context=context)
        _logger.debug("UID : %s", str(uid))
        forbidden_days = order.get_forbidden_days()  

        min_date = order.get_min_date(forbidden_days=forbidden_days) 
        #[year, month, day, hour, minutes]
        max_date = order.get_max_date(min_date=min_date, forbidden_days=forbidden_days)  
        forbidden_intervals = order.get_forbidden_time_intervals(min_date=min_date, max_date=max_date) 
        return {
            'min_date' : min_date,
            'max_date' : max_date,
            'forbidden_days' : forbidden_days,
            'forbidden_intervals' : forbidden_intervals,
            'format' : order.get_datetime_format()
            }  
