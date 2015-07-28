# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp
import logging
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)


class DeliveryGrid(osv.osv):
    _name = "delivery.grid"
    _inherit = "delivery.grid"
    
    _columns = {
        'zip_list' : fields.text(string="Zip code list", help="This grid will only be used for delivery with a zip code in that list. Example : '1000,1020,1040'", translate=False),
        'notif_partner_id' : fields.many2one('res.partner', string="Partner to notify", help="The email address of partner will receive a copy of sale order with that delivery grid")
    }
    
    def get_zip_list(self, cr, uid, grid, context=None) :
        zip_list = grid.zip_list.split(',')
        zip_list = [int(zip) for zip in zip_list]
        return zip_list
        
    
    def _check_zip(self, cr, uid, ids, context = None) :
        grid = self.browse(cr, uid, ids, context=context)
        try:
            self.get_zip_list(cr, uid, grid, context=context)
            return True
        except:
            return False
            
    
    def _check_partner(self, cr, uid, ids, context = None) :
        grid = self.browse(cr, uid, ids, context=context)
        return bool(not grid.notif_partner_id or grid.notif_partner_id.email)
    
    _constraints = [
        (_check_zip, 'Zip code should be numbers separated by comma', ['zip_list']),
        (_check_partner, 'Partner should have an email address', ['notif_partner_id'])
        ]
    
class DeliveryCarrier(osv.osv) :
    _name = "delivery.carrier"
    _inherit = "delivery.carrier"
    
    def grid_get(self, cr, uid, ids, contact_id, context=None):
        contact = self.pool.get('res.partner').browse(cr, uid, contact_id, context=context)
        for carrier in self.browse(cr, uid, ids, context=context) :
            _logger.debug("checking carrier : %s", carrier.name)
            for grid in carrier.grids_id :
                if grid.zip_list and contact.zip and not context.get('checkout', False) : #if no contact.zip, not checked yet
                    #check address only on confirm order
                    _logger.debug("Zip code check")
                    try : 
                        contact_zip = int(contact.zip)
                    except :
                        continue
                    if contact_zip in self.pool.get('delivery.grid').get_zip_list(cr, uid, grid, context=context) :
                        _logger.debug("zip code in zip list")
                        return grid.id
                else :
                    _logger.debug("no zip code")
                    return grid.id
        return False
    
class SaleOrder(osv.osv) :
    _name = "sale.order"
    _inherit = "sale.order"
    
    def action_quotation_send(self, cr, uid, ids, context=None):
        """Overload to add related carrier grid partner to email context"""
        action_dict = super(SaleOrder, self).action_quotation_send(cr, uid, ids, context=context)
        context.update({'checkout' : False})
        for order in self.browse(cr, uid, ids, context=context) :
            carrier = order.carrier_id
            grid_id = self.pool.get('delivery.carrier').grid_get(cr, uid, [carrier.id], order.partner_shipping_id.id, context=context)
            if grid_id : #should always be true at this state
                grid = self.pool.get('delivery.grid').browse(cr, uid, [grid_id], context=context)
                if grid.notif_partner_id :
                    _logger.debug("Partner to notify from delivery grid : %s", grid.notif_partner_id.email)
                     
                    #action_dict['context'].update({'carrier_notif_partner_id' : grid.notif_partner_id.id})
                    context.update({'carrier_notif_partner_id' : grid.notif_partner_id.id})
                    _logger.debug("context : %s", context)
         
 
        return action_dict
  
#     def action_button_confirm(self, cr, uid, ids, context=None):
#         """Add related carrier grid partner to context to use in email config"""
#         _logger.debug("In action button confirm overload for delivery notification")
#         context.update({'checkout' : False})
#         for order in self.browse(cr, uid, ids, context=context) :
#             carrier = order.carrier_id
#             grid_id = self.pool.get('delivery.carrier').grid_get(cr, uid, [carrier.id], order.partner_shipping_id.id, context=context)
#             if grid_id : #should always be true at this state
#                 grid = self.pool.get('delivery.grid').browse(cr, uid, [grid_id], context=context)
#                 if grid.notif_partner_id :
#                     _logger.debug("Partner to notify from delivery grid : %s", grid.notif_partner_id.email)
#                      
#                     context = dict(context or {}, carrier_notif_partner_id = grid.notif_partner_id.id)
#                     _logger.debug("context : %s", context)
#             #Old odoo version doesn't send mail in this function
#                      
#         return super(SaleOrder, self).action_button_confirm(cr, SUPERUSER_ID, ids, context=context)

class EmailTemplate(osv.osv):
    _name = "email.template"
    _inherit = 'email.template'
    
    def generate_recipients_batch(self, cr, uid, results, template_id, res_ids, context=None) :
        """Overload to add a partner to notify from context"""
        results = super(EmailTemplate, self).generate_recipients_batch(cr, uid, results, template_id, res_ids, context=context)
        template = self.browse(cr, uid, template_id, context=context)
        _logger.debug("generate_recipients_batch")
        _logger.debug("template model : %s", template.model)
        _logger.debug('context : %s', context)
        if template.model == "sale.order" and context.get('carrier_notif_partner_id') :
            for res_id, values in results.iteritems() :
                _logger.debug("Adding partner from context to destinators : %s", results[res_id]['partner_ids'])
                results[res_id]['partner_ids'] += self.pool['res.partner'].exists(cr, SUPERUSER_ID, [context.get('carrier_notif_partner_id')], context=context)
                _logger.debug("Added : %s", results[res_id]['partner_ids'])
        return results