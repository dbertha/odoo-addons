# -*- coding: utf-8 -*-

from openerp import models, SUPERUSER_ID
from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

class ResUsers(osv.osv) :
    _name = 'res.users'
    _inherit = 'res.users'
    
    def _get_spent_amount(self, cr, uid, ids, field_name, arg, context=None) :
        _logger.debug("In get spent amount")
        sale_order_obj = self.pool.get("sale.order")
        res = {}
        for user in self.browse(cr, SUPERUSER_ID, ids, context=context) :
            if not user.portal_group_id :
                res[user.id] = 0.0
            else :
                _logger.debug("user partner id : %s", user.partner_id.id)
                sale_order_ids = sale_order_obj.search(cr, SUPERUSER_ID, [('partner_id', '=', user.partner_id.id),
                                           ('portal_group_id', '=', user.portal_group_id.id),
                                           ('state', 'not in', ['draft','canceled', 'sent'])], context=context)
                spend_amount = 0.0
                for so in sale_order_obj.browse(cr, SUPERUSER_ID, sale_order_ids, context=context) :
                    spend_amount += so.amount_total
                res[user.id] = spend_amount
        _logger.debug("spend amount : %s", res)
        return res
            
    _columns = {
        'portal_group_id' : fields.many2one('res.users.groups', string="Portal Group"),
        #'given_amount' : fields.float(string="Amount given by administrator"),
        #'available_amount' : fields.(_get_available_amount, type="float", string="Available amount"),
        'spent_amount' : fields.function(_get_spent_amount, type='float', string="Spent Amount", store=True, digits_compute=dp.get_precision('Account')),
        'available_amount' : fields.float(string="Available amount"),
        'credit_tag' : fields.many2one('account.credit.tag', string="Credit Tag")
    }
    
    def _get_group(self,cr, uid, context=None):
        _logger.debug("In overloaded get group")
        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid, context=context)
        dataobj = self.pool.get('ir.model.data')
        try:
            
            dummy,group_admin_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'portal_sale_group', 'group_portal_admins')
            if group_admin_id in [group.id for group in user.groups_id] :
                dummy,group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'portal_sale_group', 'group_portal_users')
                dummy,group_portal_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_portal')
                _logger.debug("Portal group found and fixed")
                return [group_portal_id,group_id]
        except ValueError :
            pass
        return super(ResUsers, self)._get_group(cr, uid, context=context)
    
    def _get_invoice_street(self,cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid, context=context)
        dataobj = self.pool.get('ir.model.data')
        try:
            
            dummy,group_admin_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'portal_sale_group', 'group_portal_admins')
            if group_admin_id in [group.id for group in user.groups_id] :
                return user.street
        except ValueError :
            pass
        return ""
    
    def _get_country(self,cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid, context=context)
        dataobj = self.pool.get('ir.model.data')
        try:
            
            dummy,group_admin_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'portal_sale_group', 'group_portal_admins')
            if group_admin_id in [group.id for group in user.groups_id] :
                return user.country_id.id
        except ValueError :
            pass
        return None
    
    def _get_state(self,cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid, context=context)
        dataobj = self.pool.get('ir.model.data')
        try:
            
            dummy,group_admin_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'portal_sale_group', 'group_portal_admins')
            if group_admin_id in [group.id for group in user.groups_id] :
                return user.state_id.id
        except ValueError :
            pass
        return None
    
    def _get_zip(self,cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid, context=context)
        dataobj = self.pool.get('ir.model.data')
        try:
            
            dummy,group_admin_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'portal_sale_group', 'group_portal_admins')
            if group_admin_id in [group.id for group in user.groups_id] :
                return user.zip
        except ValueError :
            pass
        return ""
    
    def _get_city(self,cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid, context=context)
        dataobj = self.pool.get('ir.model.data')
        try:
            
            dummy,group_admin_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'portal_sale_group', 'group_portal_admins')
            if group_admin_id in [group.id for group in user.groups_id] :
                return user.city
        except ValueError :
            pass
        return ""
    
    _defaults = {
        'groups_id': _get_group,
        'street2' : _get_invoice_street,
        'country_id' : _get_country,
        'state_id' : _get_state,
        'zip'  : _get_zip,
        'city' : _get_city
    }