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
