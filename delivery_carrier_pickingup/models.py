# -*- coding: utf-8 -*-

from openerp import models, fields, SUPERUSER_ID, api, _
import logging

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model) :
    _name = "delivery.carrier"
    _inherit = "delivery.carrier"

    is_pickup = fields.Boolean(string='Is a shop pick-up', 
            help='if activated, the address of delivery_method will be used as shipping address')
    shop_location = fields.Many2one('stock.location', string="Stock Location", 
            help="If it's a picking in shop, the address of the stock will be used as shipping address. "+ 
            "If no pickup, this field can still be used to store an email address to be notified when this delivery carrier is used")
    address_partner = fields.Many2one('res.partner', related ="shop_location.partner_id", store=True, string="Address", 
            help="Address to use as shipping address."+ 
            "If no pickup, this field can still be used to store an email address to be notified when this delivery carrier is used")
    
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def delivery_set(self):
        result = super(SaleOrder, self).delivery_set()
        if result :
            for order in self: 
                carrier = order.carrier_id
                vals = {}
                if carrier.is_pickup and carrier.shop_location :
                    warehouse_ids = self.env['stock.warehouse'].search([('lot_stock_id.id','=',carrier.shop_location.id)])
                    if warehouse_ids :
                        vals['warehouse_id'] = warehouse_ids[0].id
                    if carrier.address_partner :
                        vals['partner_shipping_id'] = carrier.address_partner.id
                else :
                    vals['warehouse_id'] = self.env['ir.model.data'].get_object('stock', 'warehouse0').id
                order.write(vals)
        return result