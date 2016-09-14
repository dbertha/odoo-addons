# -*- coding: utf-8 -*-
import werkzeug

from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug
from openerp.addons.web.controllers.main import login_redirect
import openerp.addons.website_sale_delivery_condition.controllers.main
import logging



_logger = logging.getLogger(__name__)
class website_sale(openerp.addons.website_sale_delivery_condition.controllers.main.website_sale):

    @http.route(['/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>',
        '/shop/type/<model("delivery.condition"):condition>', #new shop requests
        '/shop/type/<model("delivery.condition"):condition>/page/<int:page>',
        '/shop/type/<model("delivery.condition"):condition>/category/<model("product.public.category"):category>',
        '/shop/type/<model("delivery.condition"):condition>/category/<model("product.public.category"):category>/page/<int:page>'
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, condition=None, search='', **post):
        """Overload to redirect to menu page"""
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        if category and not condition :
            categ = request.registry['product.public.category'].browse(cr, SUPERUSER_ID, int(category), context=context)
            condition = categ.condition_id
        if not category and not condition :
            return request.redirect("/page/nos-cartes")
        else :
            return super(website_sale, self).shop(page, category, condition, search, **post)