# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp import models
from openerp.osv import osv, fields
from openerp.addons.web.http import request

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import pytz
from pytz import timezone

import logging

_logger = logging.getLogger(__name__)
#TODO : superuser ID

class sale_configuration(osv.osv_memory):
    _inherit = 'sale.config.settings'

    _columns = {
        'current_week_number': fields.selection(
                [(1, 'Week 1'), (2, 'Week 2'), (3, 'Week 3'), (4, 'Week 4')],
                string="Current week number :",
                help="Choose the current week for rotating products.", 
            )
    }
    
    def set_current_week_number(self, cr, uid, ids, context=None):
        product_template_objs = self.pool['product.template']
        for record in self.browse(cr, uid, ids, context=context):
            product_template_objs.reset_week_published(cr, uid, [0], context=context)
            product_template_objs.publish_tagged_products(cr, uid, [0], record.current_week_number, context=context)
            
        
    def get_default_current_week_number(self, cr, uid, ids, context=None):
        product_template_objs = self.pool['product.template']
        current_week = product_template_objs.get_current_week(cr, uid, [0], context=None)
        return {'current_week_number': current_week or None}
    
class product_template(osv.Model):
    _inherit = 'product.template'
    
    _columns = {
        'week_number': fields.selection(
                [(1, 'Week 1'), (2, 'Week 2'), (3, 'Week 3'), (4, 'Week 4')],
                string="Number of the week of publication :",
                help="Choose the week when this product should be published. Left blank if not rotating", 
            )
    }
    
    def get_current_week(self, cr, uid, ids, context=None): 
        """Return week number whose articles are currently published.
        Assert : the published articles with a week number att have all the same week number
        """
        product_ids = self.search(cr, uid, [('website_published', '=', True)], context=context)
        for product in self.browse(cr, uid, product_ids, context=context) :
            _logger.debug("article tested : %s with number %s", product.name, str(product.week_number))
            if product.week_number :
                _logger.debug("current week found : %d", product.week_number)
                return product.week_number
        return False
    
    def reset_week_published(self, cr, uid, ids, context=None):
        """Set the published attribute of all products with a week number to False"""
        product_ids = self.search(cr, uid, [('website_published', '=', True)], context=context)
        for product in self.browse(cr, uid, product_ids, context=context) :
            if product.week_number :
                product.write({'website_published' : False})
    
    def publish_tagged_products(self, cr, uid, ids, weeknumber, context=None):
        """Set the published attribute of the product of that weeknumber to True"""
        product_ids = self.search(cr, uid, 
                            [('website_published', '=', False), ('week_number', '=', weeknumber)], context=context)
        _logger.debug("number of articles with week %d : %d", weeknumber, len(product_ids))
        for product in self.browse(cr, uid, product_ids, context=context) :
            product.write({'website_published' : True})
    
    def tick(self, cr, uid, ids=[0], context=None):
        """One tick in the rotation
        For good behavior, assert that there is a least one article for each of
        the possible week number (this is how we store the current week number)"""
        current_week = self.get_current_week(cr, uid, ids, context)
        _logger.debug("current week : %d", current_week)
        self.reset_week_published(cr, uid, ids, context)
        if(current_week):
            new_current_week = 1 + (current_week % 4) #1,2,3,4
            self.publish_tagged_products(cr, uid, ids, new_current_week, context)
            
    def onchange_week_number(self, cr, uid, ids, new_week_number, context=None):
        current_week = self.get_current_week(cr, uid, ids, context)
        _logger.debug("current week : %d, new week_number : %d", current_week, new_week_number)
        #week_number = None #TODO
        if(current_week == new_week_number) :
           return {'value': {
            'website_published': True,
        }}
        elif(new_week_number != 0) :
            _logger.debug("article should be unpublished")
            return {'value': {
            'website_published': False,
        }}
        return {'value': {}}
        
    def is_rotating(self, cr, uid, ids, context=None):
        """Expect only one ID"""
        for product in self.browse(cr, uid, ids, context=context) :
            return product.week_number
        
