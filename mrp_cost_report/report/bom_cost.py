# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, models
from openerp.osv import fields, osv


class mrp_bom(osv.osv):
    """
    Defines bills of material for a product.
    """
    _name = 'mrp.bom'
    _inherit = 'mrp.bom'

    def _prepare_consume_line(self, cr, uid, bom_line_id, quantity, context=None):
        #"""add custom fields"""
        res = super(mrp_bom,self)._prepare_consume_line(cr, uid, bom_line_id, quantity, context=context)
        res.update({'x_percentage' : bom_line_id.x_percentage})
        return res


class MrpBomCost(models.AbstractModel):
    _name = 'report.mrp_bom_cost'
    _inherit = 'report.mrp_bom_cost'

    @api.multi
    def get_lines(self, boms):
        product_lines = []
        for bom in boms:
            products = bom.product_id
            if not products:
                products = bom.product_tmpl_id.product_variant_ids
            for product in products:
                attributes = []
                for value in product.attribute_value_ids:
                    attributes += [(value.attribute_id.name, value.name)]
                result, result2 = self.env['mrp.bom']._bom_explode(bom, product, 1)
                product_line = {'name': product.name, 
                                'lines': [], 
                                'total': 0.0,
                                'currency': self.env.user.company_id.currency_id,
                                'product_uom_qty': bom.product_qty,
                                'product_uom': bom.product_uom,
                                'attributes': attributes,
                                'main_work_center' : bom.routing_id and \
                                    bom.routing_id.workcenter_lines and \
                                    bom.routing_id.workcenter_lines[0].workcenter_id.name or '',
                                }
                total = 0.0
                for bom_line in result:
                    line_product = self.env['product.product'].browse(bom_line['product_id'])
                    price_uom = self.env['product.uom']._compute_qty(line_product.uom_id.id, line_product.standard_price, bom_line['product_uom'])
                    line = {
                        'percentage': bom_line.x_percentage,
                        'product_id': line_product,
                        'seller' : line_product.seller_ids and line_product.seller_ids[0].display_name or '',
                        'product_uom_qty': bom_line['product_qty'],
                        'product_uom': self.env['product.uom'].browse(bom_line['product_uom']),
                        'price_unit': price_uom,
                        'total_price': price_uom * bom_line['product_qty'],
                    }
                    total += line['total_price']
                    product_line['lines'] += [line]
                product_line['total'] = total
                product_lines += [product_line]
        return product_lines

#     @api.multi
#     def render_html(self, data=None):
#         boms = self.env['mrp.bom'].browse(self.ids)
#         res = self.get_lines(boms)
#         return self.env['report'].render('mrp.mrp_bom_cost', {'lines': res})