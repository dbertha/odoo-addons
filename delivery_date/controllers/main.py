# -*- coding: utf-8 -*-
import werkzeug

from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug
from openerp.addons.web.controllers.main import login_redirect
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
        values = super(website_sale, self).checkout_values(data)
        values['checkout'].update(self._parse_delivery_date(data))
        #_logger.debug("checkout value end, checkout delivery datetime start : %s", values['checkout']['delivery_datetime_start'])
        return values
        
    def _parse_delivery_date(self, data):
        if data and data.get('delivery_date') :
            tzone = timezone('Europe/Brussels')
            delivery_interval_time = timedelta(minutes=30)
            _logger.debug("checkout value delivery_date : %s", data.get('delivery_date'))
            splitted = data['delivery_date'].split()
            if(len(splitted) != 3) :
                _logger.error("Datetime sould be in format Day DD/MM/YYYY HH:MM : %s", splitted)
                return {}
            date = splitted[1].split('/')
            if(len(date) != 3) :
                _logger.error("Date should be in format DD/MM/YYYY : %s", date)
                return {}
            try:
                day,month,year = int(date[0]), int(date[1]), int(date[2])
            except : 
                _logger.error("Date values are not integers")
                return {}
            interval_start = splitted[2].split(':')
            if(len(interval_start) != 2) :
                _logger.error("Time should be in format HH:MM : %s", splitted)
                return {}
            _logger.debug("interval_start : %s", interval_start)
            try:
                datetime_start = datetime(year, month, day, int(interval_start[0]), int(interval_start[1]))
            except :
                _logger.error("checkout values : exception in datetime creation")
                return {}
            datetime_start = tzone.localize(datetime(year, month, day, int(interval_start[0]), int(interval_start[1]))).astimezone (pytz.utc)
            _logger.debug("checkout value end, checkout delivery datetime start : %s", datetime_start)

            return {'delivery_datetime_start' : datetime_start,
                'delivery_datetime_end' : datetime_start + delivery_interval_time }
        return {}

    def checkout_form_save(self, checkout):
        """overload to store delivery date"""
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry

        order = request.website.sale_get_order(force_create=1, context=context)

        order_obj = registry.get('sale.order')
        
        super(website_sale, self).checkout_form_save(checkout)

        #need to add delivery date
        _logger.debug("checkout form save, before write : checkout delivery date time start : %s", checkout.get('delivery_datetime_start'))
        order_info = {'requested_delivery_datetime_start' : checkout.get('delivery_datetime_start'),
                      'requested_delivery_datetime_end' : checkout.get('delivery_datetime_end')
                      }
        
        order_obj.write(cr, SUPERUSER_ID, [order.id], order_info, context=context)

    def check_date_validity(self, date_time):
        tzone = timezone('Europe/Brussels')
        datetime_start = date_time.astimezone(tzone)        
        uid = request.session.uid
        context = request.session.context
        cr = request.cr
        order_id = request.session.get('sale_order_id')
        return request.registry['sale.order'].check_date(cr,uid, order_id,datetime_start,context=context)
        
    def checkout_form_validate(self, data):
        _logger.debug("Validating form")
        error = super(website_sale, self).checkout_form_validate(data)
        if not data.get("delivery_datetime_start") : 
            _logger.debug("form validate : delivery date missing")
            error['delivery_date'] = 'missing'
        elif not self.check_date_validity(data.get('delivery_datetime_start')) :
            _logger.debug("form validate : delivery date not correct")
            error['delivery_date'] = 'notAcceptable'
        _logger.debug("form validate : error : %s", str(error))
        return error
    
    @http.route('/shop/checkout/get_dates', type='json', auth="public")
    def get_dates(self):
        uid = request.uid
        context = request.context
        cr = request.cr
        sale_order_obj = request.registry['sale.order']
        order_id = request.session.get('sale_order_id')
        _logger.debug("UID : %s", str(uid))
        min_date = sale_order_obj.get_min_date(cr,uid, order_id, context) 
        #[year, month, day, hour, minutes]
        max_date = sale_order_obj.get_max_date(cr,uid, order_id, context)  
        forbidden_days = sale_order_obj.get_forbidden_days(cr,uid, order_id, context)  
        forbidden_intervals = sale_order_obj.get_forbidden_time_intervals(cr,uid, order_id, min_date=min_date, max_date=max_date, context=context) 
        return {
            'min_date' : min_date,
            'max_date' : max_date,
            'forbidden_days' : forbidden_days,
            'forbidden_intervals' : forbidden_intervals
            }  
