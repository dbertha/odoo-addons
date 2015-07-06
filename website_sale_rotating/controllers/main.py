# -*- coding: utf-8 -*-
import werkzeug

from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug
from openerp.addons.web.controllers.main import login_redirect
import openerp.addons.website_sale.controllers.main
from openerp.addons.website_sale.controllers.main import QueryURL, PPG, PPR, table_compute
import logging


_logger = logging.getLogger(__name__)

#TODO : checkout : articles from sale order should not have different week_numbers
#and should still be published