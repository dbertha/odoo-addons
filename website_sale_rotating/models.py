# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp import models
from openerp import api, fields, models, _
import random


import logging

_logger = logging.getLogger(__name__)
#TODO : superuser ID

class sale_configuration(models.TransientModel):
    _inherit = 'sale.config.settings'


    current_week_number = fields.Selection(
                [(1, 'Week 1'), (2, 'Week 2'), (3, 'Week 3'), (4, 'Week 4')],
                string="Current week number :",
                help="Choose the current week for rotating products.", 
            )
    
    @api.multi
    def set_current_week_number(self) :
        self.ensure_one()
        product_template_objs = self.env['product.template']
        product_template_objs.reset_week_published()
        if self.current_week_number :
            product_template_objs.publish_tagged_products(self.current_week_number)
            
    @api.model
    def get_default_current_week_number(self, fields):
        product_template_objs = self.env['product.template']
        current_week = product_template_objs.get_current_week()
        return {'current_week_number': current_week or None}
    
class product_template(models.Model):
    _inherit = 'product.template'
    
    week_number = fields.Selection(
                [(1, 'Week 1'), (2, 'Week 2'), (3, 'Week 3'), (4, 'Week 4')],
                string="Number of the week of publication :",
                help="Choose the week when this product should be published. Left blank if not rotating", 
            )
    
    
    @api.model
    def get_current_week(self): 
        """Return week number whose articles are currently published.
        Assert : the published articles with a week number att have all the same week number
        """
        product_ids = self.search([('website_published', '=', True)])
        for product in product_ids :
            _logger.debug("article tested : %s with number %s", product.name, str(product.week_number))
            if product.week_number :
                _logger.debug("current week found : %d", product.week_number)
                return product.week_number
        return False
    @api.model
    def reset_week_published(self):
        """Set the published attribute of all products with a week number to False"""
        products = self.search(['&', ('website_published', '=', True), ('week_number', '!=', False)])
        products.write({'website_published' : False})

    @api.model
    def publish_tagged_products(self, weeknumber):
        """Set the published attribute of the product of that weeknumber to True"""
        product_ids = self.search( 
                            [('website_published', '=', False), ('week_number', '=', weeknumber)])
        #custom : elect some products to be the boxes content
        plats_ids = self.search(
                            ['&',('website_published', '=', False), '&', 
                             ('week_number', '=', weeknumber), ('public_categ_ids', 'in', [24])]).ids
        entrees_ids = self.search(
                            ['&',('website_published', '=', False), '&', 
                             ('week_number', '=', weeknumber), ('public_categ_ids', 'in', [22])]).ids
        _logger.debug("plats : %s", plats_ids)
        _logger.debug("entrees : %s", entrees_ids)
        chosen_plats_ids = random.sample(plats_ids, 7)
        chosen_entrees_ids = random.sample(entrees_ids, 7)
        fr_context = dict(self.env.context)
        fr_context['lang'] = 'fr_BE'
        nl_context = dict(self.env.context)
        nl_context['lang'] = 'nl_NL'
        entrees_desc_nl = u'WEEK ' + unicode(weeknumber) + u'\nVOORGERECHTEN : \n'
        plats_desc_nl = u'\nHOOFDGERECHTEN : \n'
        entrees_desc_fr = u'SEMAINE ' + unicode(weeknumber) + u'\nLes entrées de la semaine : \n'
        plats_desc_fr = u'\nLes plats de la semaine : \n'
        for index in range(0,3) :
            name = self.browse([chosen_entrees_ids[index]]).name
            _logger.debug("entree name type : %s # %s", name, type(name))
            entrees_desc_fr += self.with_context(fr_context).browse(chosen_entrees_ids[index]).name + u'\n'
            plats_desc_fr += self.with_context(fr_context).browse(chosen_plats_ids[index]).name + u'\n'
            entrees_desc_nl += self.with_context(nl_context).browse(chosen_entrees_ids[index]).name + u'\n'
            plats_desc_nl += self.with_context(nl_context).browse(chosen_plats_ids[index]).name + u'\n'
        self.with_context(fr_context).browse([38001]).write({'description_sale' : entrees_desc_fr + plats_desc_fr, 'x_web_description' : entrees_desc_fr + plats_desc_fr}) #Box 3/7
        self.with_context(nl_context).browse([38001]).write({'description_sale' : entrees_desc_nl + plats_desc_nl, 'x_web_description' : entrees_desc_nl + plats_desc_nl}) #Box 3/7
        for index in range(3,5) :
            entrees_desc_fr += self.with_context(fr_context).browse(chosen_entrees_ids[index]).name + u'\n'
            plats_desc_fr += self.with_context(fr_context).browse(chosen_plats_ids[index]).name + u'\n'
            entrees_desc_nl += self.with_context(nl_context).browse(chosen_entrees_ids[index]).name + u'\n'
            plats_desc_nl += self.with_context(nl_context).browse(chosen_plats_ids[index]).name + u'\n'
        self.with_context(fr_context).browse([38002]).write({'description_sale' : entrees_desc_fr + plats_desc_fr, 'x_web_description' : entrees_desc_fr + plats_desc_fr}) #Box 5/7
        self.with_context(nl_context).browse([38002]).write({'description_sale' : entrees_desc_nl + plats_desc_nl, 'x_web_description' : entrees_desc_nl + plats_desc_nl}) #Box 5/7
        for index in range(5,7) :
            entrees_desc_fr += self.with_context(fr_context).browse(chosen_entrees_ids[index]).name + u'\n'
            plats_desc_fr += self.with_context(fr_context).browse(chosen_plats_ids[index]).name + u'\n'
            entrees_desc_nl += self.with_context(nl_context).browse(chosen_entrees_ids[index]).name + u'\n'
            plats_desc_nl += self.with_context(nl_context).browse(chosen_plats_ids[index]).name + u'\n'
        self.with_context(fr_context).browse([38180]).write({'description_sale' : entrees_desc_fr + plats_desc_fr, 'x_web_description' : entrees_desc_fr + plats_desc_fr}) #Box 7/7
        self.with_context(nl_context).browse([38180]).write({'description_sale' : entrees_desc_nl + plats_desc_nl, 'x_web_description' : entrees_desc_nl + plats_desc_nl}) #Box 7/7

        #end custom
        _logger.debug("number of articles with week %d : %d", weeknumber, len(product_ids))
        #TODO : more efficient : write method with ids
        product_ids.write({'website_published' : True})
    @api.model
    def tick(self):
        """One tick in the rotation
        For good behavior, assert that there is a least one article for each of
        the possible week number"""
        current_week = self.get_current_week()
        _logger.debug("current week : %d", current_week)
        self.reset_week_published()
        if(current_week):
            new_current_week = 1 + (current_week % 4) #1,2,3,4
            self.publish_tagged_products(new_current_week)
    
    @api.onchange('week_number')
    def onchange_week_number(self):
        if self.week_number :
            current_week = self.get_current_week()
            _logger.debug("current week : %d, new week_number : %d", current_week, self.week_number)
            #week_number = None #TODO
            if(current_week == self.week_number) :
               self.website_published = True
            elif(self.week_number != 0) :
                _logger.debug("article shouldn't be published")
                self.website_published = False
        
    def is_rotating(self):
        """Expect only one ID"""
        return self.week_number
        
class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = "sale.order"
    
    def check_products_availability(self) :
        """Check if the rotating products in cart are published,
        remove them elsewhere. Those products were added when published but now they are
        not anymore and we can't accept a cart with them"""
        _logger.debug('checking product availability')
        ids_to_remove = []
        for line in self.order_line :
            if not line.is_delivery : #delivery can be unpublished
                if line.product_id.product_tmpl_id.week_number and not line.product_id.product_tmpl_id.website_published :
                    #not ok
                    _logger.debug("Will remove line : %s", line.name)
                    ids_to_remove.append(line.id)
        if ids_to_remove :
            self.env['sale.order.line'].sudo().unlink(ids_to_remove)
        return bool(ids_to_remove)