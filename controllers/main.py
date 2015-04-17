# -*- coding: utf-8 -*-
import werkzeug

from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug
from openerp.addons.web.controllers.main import login_redirect
import openerp.addons.website_sale.controllers.main
import logging


_logger = logging.getLogger(__name__)
class website_sale(openerp.addons.website_sale.controllers.main.website_sale):

    def checkout_redirection(self, order):
        if order.amount_total < 5.00 : #should not be less than 5.00
            return request.redirect('/shop/cart')
        else :
            return super(website_sale, self).checkout_redirection(order)