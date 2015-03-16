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
class delivery_date_on_sale_order(models.Model):
    _name = "sale.order"
    _inherit = 'sale.order'
    _columns = {
        #'requested_delivery_date' : fields.date(string='Requested Delivery Date', help="Date requested by the customer for the delivery."),
        'requested_delivery_datetime_start' : fields.datetime(string='Requested Delivery Interval Beginning',
            help='The begin of the time interval requested for the delivery'),
        'requested_delivery_datetime_end' : fields.datetime(string='Requested Delivery Interval Ending',
            help='The end of the time interval requested for the delivery')
    }
    def getDeliveryDates(self, cr, uid, ids, context=None):
        sale_order_obj = self.pool['sale.order']
        sale_order_id = request.session.get('sale_order_id')
        sale_order = sale_order_obj.browse(cr, SUPERUSER_ID, sale_order_id, context=context)
        nb_dates = 15
        max_delay = 0 #pick-up today is allowed
        #for line in order_line : #TODO : get product_id for each line, get products based on ID
        #    maxDelay = max(line.delivery_delay, max_delay)
        #(line.product_id.type == "service" for line in order.website_order_line)
        date_today = date.today()
        tzone = timezone('Europe/Brussels')
        now = pytz.utc.localize(datetime.now()).astimezone(tzone)
        if now.hour >= 18 : #shop close
            max_delay += 1
        delta = timedelta(days=max_delay)
        delta_one_day = timedelta(days=1)
        result = []
        for i in range(nb_dates) :
            result.append((date_today + delta).strftime("%a %d/%m/%Y"))
            delta += delta_one_day
        return result

# class product_attribute_delivery_delay(models.Model):
#     _name = "product.template"
#     _inherit = 'product.template'
#     _columns = {
#         'delivery_delay': fields.integer(string='Delivery Delay',
#             help='The delay for the product to be ready for delivery after been bought')
#     }
#     _defaults = {
#                  'delivery_delay' : 1 #delivery next day
#                  }
#     
#     
#     def _check_value(self, cr, uid, ids, context=None): #sould be a natural
#         obj = self.browse(cr, uid, ids[0], context=context)
#         if obj.delivery_delay < 0:
#             return False
#         return True
#     _constraints = [
#         (_check_value, 'Delay sould be equal or greater than 0!', ['delivery_delay'])
#     ]
    
#class SaleOrder(models.Model):
#    _inherit = 'sale.order'
    
#     def _get_website_data(self, cr, uid, order, context=None):
#         """ Override to add date of delivery-related website data. """
#         values = super(SaleOrder, self)._get_website_data(cr, uid, order, context=context)
#         
#         # We need a delivery date only if we have stockable products
#         has_stockable_products = False
#         for line in order.order_line:
#             if line.product_id.type in ('consu', 'product'):
#                 has_stockable_products = True
#         if not has_stockable_products:
#             return values
# 
#         values['acceptable_delivery_datetimes'] = ["Une date ..."]
#         return values
    
    
    
    
#     def calc_date(self, cr, uid, context=None): #recordSet ssi héritage de osv.Model : différence avec osv.osv ?
#         """Compute the limit date for a given date"""
#         if context is None:
#             context = {}
#         if not context.get('product_id', False):
#             date = False #TODO : return (False, False) ?
#         else:
#             product = openerp.registry(cr.dbname)['product.product'].browse(
#                     cr, uid, context['product_id'])
#             duration = getattr(product, 'delivery_delay')
#             #Une commande passée après 16h est considérée comme passée le lendemain (car livraison ce lendemain impossible)
#             one_day_more = datetime.datetime.today().getHour() >= 16 #TODO : vérifier doc, DEFINE
#             date = datetime.datetime.today() + datetime.timedelta(days=duration)
#             if one_day_more :
#                 date += datetime.timedelta(days=1)
#         return (date, one_day_more) #TODO date est une datetime : à transformer en fields.Date
        
    #TODO : tests
    
    
#class product_attribute_price(osv.osv):
#    _name = "product.attribute.price"
#    _columns = {
#        'product_tmpl_id': fields.many2one('product.template', 'Product Template', required=True, ondelete='cascade'),
#        'value_id': fields.many2one('product.attribute.value', 'Product Attribute Value', required=True, ondelete='cascade'),
#        'price_extra': fields.float('Price Extra', digits_compute=dp.get_precision('Product Price')),
#    }
