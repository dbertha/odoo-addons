# -*- coding: utf-8 -*-

import traceback
from openerp.osv import osv
import openerp.addons.decimal_precision as dp
import logging
from openerp import SUPERUSER_ID

from openerp import api, fields, models, _


_logger = logging.getLogger(__name__)

class DeliveryGridZips(models.Model):
    _name = "delivery.zips"
    _order = 'zip_from'


    @api.multi
    @api.depends('name','zip_from', 'zip_to')
    def name_get(self):
        result = []
        for ziplist in self:
            name = ""
            if ziplist.zip_from and ziplist.zip_to :
                name = ziplist.zip_from + ' - ' + ziplist.zip_to
            ziplist.name = name
            result.append((ziplist.id, name))
        return result

    zip_from = fields.Char('Zip From')
    zip_to = fields.Char('Zip To')
    name = fields.Char(compute="name_get")

    

    @api.multi
    @api.constrains('zip_from', 'zip_to')
    def _check_order(self):
        for ziplist in self:
            if ziplist.zip_from > ziplist.zip_to :
                raise ValueError(_('The zip from value is higher than the zip to value.'))


class DeliveryCarrier(models.Model):
    _name = "delivery.carrier"
    _inherit = "delivery.carrier"
    

    zip_ids = fields.Many2many('delivery.zips', 'delivery_carrier_zips_default_rel',
        'carrier_id', 'zip_id', string='Allowed Zip Ranges')
    notif_partner_id = fields.Many2one('res.partner', string="Partner to notify", help="The email address of partner will receive a copy of sale order with that delivery carrier")
    
    @api.multi
    def verify_carrier(self, contact):
        res = super(DeliveryCarrier, self).verify_carrier(contact)
        if res and self.zip_ids and contact and contact.zip and not self.env.context.get('checkout', False) :
            _logger.debug(contact.zip)
            res = False
            for zip_elem in self.zip_ids :
                if zip_elem.zip_from < (contact.zip or '') < zip_elem.zip_to :
                    res = self
        return res

#add ${object.carrier_id and object.carrier_id.notif_partner_id and object.carrier_id.notif_partner_id.id or ''} to email_to clause of template
