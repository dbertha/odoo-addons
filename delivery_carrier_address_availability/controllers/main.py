# -*- coding: utf-8 -*-
import werkzeug

from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug
import openerp.addons.website_sale_delivery_on_checkout.controllers.main
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone
import pytz
import logging

_logger = logging.getLogger(__name__)

class website_sale(openerp.addons.website_sale.controllers.main.website_sale):
    def checkout_form_validate(self, data):
        error, error_message = super(website_sale, self).checkout_form_validate(data)
        order = request.website.sale_get_order()
        if order.carrier_id :
            if order.partner_shipping_id :
                old_zip = order.partner_shipping_id.zip
                order.partner_shipping_id.zip = data.get("zip", False)
            res = order.carrier_id.verify_carrier(order.partner_shipping_id)

            if order.partner_shipping_id :
                order.partner_shipping_id.zip = old_zip
            if not res :
                error['carrier_id'] = 'unavailable'
                error_message.append(_('The delivery method is not available for your shipping address'))
        return error, error_message