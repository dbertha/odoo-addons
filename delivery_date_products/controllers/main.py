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
        _logger.debug("checkout value overload for delivery date parsing")
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
                _logger.debug("checkout value splitted not 3 : %s", splitted)
                return {}
            date = splitted[1].split('/')
            if(len(date) != 3) :
                _logger.debug("date value splitted not 3 : %s", date)
                return {}
            try:
                day,month,year = int(date[0]), int(date[1]), int(date[2])
            except : 
                _logger.debug("checkout value int conversion failed")
                return {}
            interval_start = splitted[2].split(':')
            if(len(interval_start) != 2) :
                _logger.debug("checkout value interval_start not 2 : %s", splitted)
                return {}
            _logger.debug("interval_start : %s", interval_start)
            try:
                datetime_start = datetime(year, month, day, int(interval_start[0]), int(interval_start[1]))
            except :
                _logger.debug("checkout values : exception in datetime creation")
                return {}
            datetime_start = tzone.localize(datetime(year, month, day, int(interval_start[0]), int(interval_start[1]))).astimezone (pytz.utc)
            _logger.debug("checkout value end, checkout delivery datetime start : %s", datetime_start)

            return {'delivery_datetime_start' : datetime_start,
                'delivery_datetime_end' : datetime_start + delivery_interval_time }
        return {}

    def checkout_form_save(self, checkout):
        _logger.debug("checkout form save")
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry

        order = request.website.sale_get_order(force_create=1, context=context)

        orm_partner = registry.get('res.partner')
        orm_user = registry.get('res.users')
        order_obj = request.registry.get('sale.order')

        partner_lang = request.lang if request.lang in [lang.code for lang in request.website.language_ids] else None

        billing_info = {}
        if partner_lang:
            billing_info['lang'] = partner_lang
        billing_info.update(self.checkout_parse('billing', checkout, True))

        # set partner_id
        partner_id = None
        if request.uid != request.website.user_id.id:
            partner_id = orm_user.browse(cr, SUPERUSER_ID, uid, context=context).partner_id.id
        elif order.partner_id:
            user_ids = request.registry['res.users'].search(cr, SUPERUSER_ID,
                [("partner_id", "=", order.partner_id.id)], context=dict(context or {}, active_test=False))
            if not user_ids or request.website.user_id.id not in user_ids:
                partner_id = order.partner_id.id

        # save partner informations
        if partner_id and request.website.partner_id.id != partner_id:
            orm_partner.write(cr, SUPERUSER_ID, [partner_id], billing_info, context=context)
        else:
            # create partner
            partner_id = orm_partner.create(cr, SUPERUSER_ID, billing_info, context=context)

        # create a new shipping partner
        _logger.debug("Form save : Shipping id=%d", checkout.get('shipping_id'))
        if checkout.get('shipping_id') == -1:
            _logger.debug("Recording shipping address")
            shipping_info = {}
            if partner_lang:
                shipping_info['lang'] = partner_lang
            shipping_info.update(self.checkout_parse('shipping', checkout, True))
            shipping_info['type'] = 'delivery'
            shipping_info['parent_id'] = partner_id
            checkout['shipping_id'] = orm_partner.create(cr, SUPERUSER_ID, shipping_info, context)

        order_info = {
            'partner_id': partner_id,
            'message_follower_ids': [(4, partner_id), (3, request.website.partner_id.id)],
            'partner_invoice_id': partner_id,
        }
        order_info.update(order_obj.onchange_partner_id(cr, SUPERUSER_ID, [], partner_id, context=context)['value'])
        address_change = order_obj.onchange_delivery_id(cr, SUPERUSER_ID, [], order.company_id.id, partner_id,
                                                        checkout.get('shipping_id'), None, context=context)['value']
        order_info.update(address_change)
        if address_change.get('fiscal_position'):
            fiscal_update = order_obj.onchange_fiscal_position(cr, SUPERUSER_ID, [], address_change['fiscal_position'],
                                                               [(4, l.id) for l in order.order_line], context=None)['value']
            order_info.update(fiscal_update)

        order_info.pop('user_id')
        order_info.update(partner_shipping_id=checkout.get('shipping_id') or partner_id)


        #need to add delivery date
        _logger.debug("checkout form save, before write : checkout delivery date time start : %s", checkout.get('delivery_datetime_start'))
        #order_info.update(requested_delivery_date = checkout.get('delivery_date'))
        order_info.update(requested_delivery_datetime_start = checkout.get('delivery_datetime_start'))
        order_info.update(requested_delivery_datetime_end = checkout.get('delivery_datetime_end'))
        #order.requested_delivery_date = checkout.get('delivery_date')
        #_logger.debug("checkout form save after write, order delivery date : %s", order.requested_delivery_date)
        
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
        if data.get('shipping_name') :
            _logger.debug("Shipping name : %s weekday : %d", data['shipping_name'], data.get('delivery_datetime_start').weekday())
            if ((data['shipping_name'] == "Uccle") and
             (data.get('delivery_datetime_start')) and (data.get('delivery_datetime_start').weekday() < 2 )) :
            #Fort Jaco closed if monday or thuesday
                error["shop_closed"] = True
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
        min_date = sale_order_obj.get_min_date(cr,uid, order_id, context) #[year, month, day, hour, minutes]
        max_date = sale_order_obj.get_max_date(cr,uid, order_id, context)  
        forbidden_days = sale_order_obj.get_forbidden_days(cr,uid, order_id, context)  
        return {
            'min_date' : min_date,
            'max_date' : max_date,
            'forbidden_days' : forbidden_days}  
            #sale_order.getMinDate() #Todo : min date as a computed field ?
            #sale_order.getForbiddenDays()
            #res = registry.get("calendar.alarm_manager").get_next_notif(cr, uid, context=context)
            #return res
    