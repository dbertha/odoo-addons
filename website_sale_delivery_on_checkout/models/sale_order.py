# -*- coding: utf-8 -*-

from openerp.osv import orm, fields
from openerp import SUPERUSER_ID
from openerp.addons import decimal_precision
from openerp.addons.web.http import request
import logging

_logger = logging.getLogger(__name__)
class delivery_carrier(orm.Model):
    _inherit = 'delivery.carrier'
    _columns = {
        'website_published': fields.boolean('Available in the website', copy=False),
        'website_description': fields.text('Description for the website'),
    }
    _defaults = {
        'website_published': True
    }


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    def _amount_all_wrapper(self, cr, uid, ids, field_name, arg, context=None):        
        """ Wrapper because of direct method passing as parameter for function fields """
        return self._amount_all(cr, uid, ids, field_name, arg, context=context)

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = super(SaleOrder, self)._amount_all(cr, uid, ids, field_name, arg, context=context)
        currency_pool = self.pool.get('res.currency')
        for order in self.browse(cr, uid, ids, context=context):
            line_amount = sum([line.price_subtotal for line in order.order_line if line.is_delivery])
            currency = order.pricelist_id.currency_id
            res[order.id]['amount_delivery'] = currency_pool.round(cr, uid, currency, line_amount)
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = {
        'amount_delivery': fields.function(
            _amount_all_wrapper, type='float', digits_compute=decimal_precision.get_precision('Account'),
            string='Delivery Amount',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The amount without tax.", track_visibility='always'
        ),
        'website_order_line': fields.one2many(
            'sale.order.line', 'order_id',
            string='Order Lines displayed on Website', readonly=True,
            domain=[('is_delivery', '=', False)],
            help='Order Lines to be displayed on the website. They should not be used for computation purpose.',
        ),
    }

    def _check_carrier_quotation(self, cr, uid, order, force_carrier_id=None, context=None):
        carrier_obj = self.pool.get('delivery.carrier')
        # check to add or remove carrier_id
        if not order:
            return False
        if all(line.product_id.type == "service" for line in order.website_order_line):
            order.write({'carrier_id': None})
            self.pool['sale.order']._delivery_unset(cr, SUPERUSER_ID, [order.id], context=context)
            return True
        else: 
            carrier_id = force_carrier_id or order.carrier_id.id
            carrier_ids = self._get_delivery_methods(cr, uid, order, context=context)
            if carrier_id:
                if carrier_id not in carrier_ids:
                    carrier_id = False
                else:
                    carrier_ids.remove(carrier_id)
                    carrier_ids.insert(0, carrier_id)
            if force_carrier_id or not carrier_id or not carrier_id in carrier_ids:
                for delivery_id in carrier_ids:
                    grid_id = carrier_obj.grid_get(cr, SUPERUSER_ID, [delivery_id], order.partner_shipping_id.id, context=context) #transmit context
                    if grid_id:
                        carrier_id = delivery_id
                        break
                order.write({'carrier_id': carrier_id})
            if carrier_id:
                self.pool['sale.order'].delivery_set(cr, SUPERUSER_ID, [order.id], context=context) #transmit context
            else:
                order._delivery_unset()                 
        _logger.debug('force carrier id : %s carrier_id : %s', force_carrier_id, carrier_id)   
        return force_carrier_id == carrier_id if force_carrier_id else bool(carrier_id)

    def _get_delivery_methods(self, cr, uid, order, context=None):
        carrier_obj = self.pool.get('delivery.carrier')
        delivery_ids = carrier_obj.search(cr, uid, [('website_published','=',True)], context=context)
        # Following loop is done to avoid displaying delivery methods who are not available for this order
        # This can surely be done in a more efficient way, but at the moment, it mimics the way it's
        # done in delivery_set method of sale.py, from delivery module
        for delivery_id in carrier_obj.browse(cr, SUPERUSER_ID, delivery_ids, context=dict(context, order_id=order.id)):
            if not delivery_id.available:
                delivery_ids.remove(delivery_id.id)
        return delivery_ids

    def _get_errors(self, cr, uid, order, context=None):
        errors = super(SaleOrder, self)._get_errors(cr, uid, order, context=context)
        if not self._get_delivery_methods(cr, uid, order, context=context):
            errors.append(('No delivery method available', 'There is no available delivery method for your order'))            
        return errors


    def _get_website_data(self, cr, uid, order, context=None):
        """ Override to add delivery-related website data. """
        values = super(SaleOrder, self)._get_website_data(cr, uid, order, context=context)
        # We need a delivery only if we have stockable products
        has_stockable_products = False
        for line in order.order_line:
            if line.product_id.type in ('consu', 'product'):
                has_stockable_products = True
        if not has_stockable_products:
            return values

        delivery_ctx = dict(context, order_id=order.id)
        DeliveryCarrier = self.pool.get('delivery.carrier')
        delivery_ids = self._get_delivery_methods(cr, uid, order, context=context)

        values['deliveries'] = DeliveryCarrier.browse(cr, SUPERUSER_ID, delivery_ids, context=delivery_ctx)
        return values

class website(orm.Model):
    _inherit = 'website'
    #override for logging :
    
    def sale_get_order(self, cr, uid, ids, force_create=False, code=None, update_pricelist=None, context=None):
        sale_order_obj = self.pool['sale.order']
        sale_order_id = request.session.get('sale_order_id')
        sale_order = None
        # create so if needed
        if not sale_order_id and (force_create or code):  
            _logger.debug("creating new order")
            # TODO cache partner_id session
            partner = self.pool['res.users'].browse(cr, SUPERUSER_ID, uid, context=context).partner_id

            for w in self.browse(cr, uid, ids):
                values = {
                    'user_id': w.user_id.id,
                    'partner_id': partner.id,
                    'pricelist_id': partner.property_product_pricelist.id,
                    'section_id': self.pool.get('ir.model.data').get_object_reference(cr, uid, 'website', 'salesteam_website_sales')[1],
                }
                sale_order_id = sale_order_obj.create(cr, SUPERUSER_ID, values, context=context)
                values = sale_order_obj.onchange_partner_id(cr, SUPERUSER_ID, [], partner.id, context=context)['value']
                sale_order_obj.write(cr, SUPERUSER_ID, [sale_order_id], values, context=context)
                request.session['sale_order_id'] = sale_order_id
        if sale_order_id:
            # TODO cache partner_id session
            partner = self.pool['res.users'].browse(cr, SUPERUSER_ID, uid, context=context).partner_id

            sale_order = sale_order_obj.browse(cr, SUPERUSER_ID, sale_order_id, context=context)
            if not sale_order.exists():
                request.session['sale_order_id'] = None
                return None
            # check for change of pricelist with a coupon
            if code and code != sale_order.pricelist_id.code:
                pricelist_ids = self.pool['product.pricelist'].search(cr, SUPERUSER_ID, [('code', '=', code)], context=context)
                if pricelist_ids:
                    pricelist_id = pricelist_ids[0]
                    request.session['sale_order_code_pricelist_id'] = pricelist_id
                    update_pricelist = True

            pricelist_id = request.session.get('sale_order_code_pricelist_id') or partner.property_product_pricelist.id

            # check for change of partner_id ie after signup
            if sale_order.partner_id.id != partner.id and request.website.partner_id.id != partner.id:
                flag_pricelist = False
                if pricelist_id != sale_order.pricelist_id.id:
                    flag_pricelist = True
                fiscal_position = sale_order.fiscal_position and sale_order.fiscal_position.id or False

                values = sale_order_obj.onchange_partner_id(cr, SUPERUSER_ID, [sale_order_id], partner.id, context=context)['value']
                if values.get('fiscal_position'):
                    order_lines = map(int,sale_order.order_line)
                    values.update(sale_order_obj.onchange_fiscal_position(cr, SUPERUSER_ID, [],
                        values['fiscal_position'], [[6, 0, order_lines]], context=context)['value'])

                values['partner_id'] = partner.id
                sale_order_obj.write(cr, SUPERUSER_ID, [sale_order_id], values, context=context)

                if flag_pricelist or values.get('fiscal_position') != fiscal_position:
                    update_pricelist = True
            # update the pricelist
            if update_pricelist:
                values = {'pricelist_id': pricelist_id}
                values.update(sale_order.onchange_pricelist_id(pricelist_id, None)['value'])
                sale_order.write(values)
                for line in sale_order.order_line:
                    sale_order._cart_update(product_id=line.product_id.id, line_id=line.id, add_qty=0)
            # update browse record
            if (code and code != sale_order.pricelist_id.code) or sale_order.partner_id.id !=  partner.id:
                sale_order = sale_order_obj.browse(cr, SUPERUSER_ID, sale_order.id, context=context)
        
        return sale_order
