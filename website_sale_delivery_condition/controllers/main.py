# -*- coding: utf-8 -*-
import werkzeug

from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug
from openerp.addons.web.controllers.main import login_redirect
import openerp.addons.website_sale.controllers.main
from openerp.addons.website_sale.controllers.main import QueryURL, PPG, PPR, table_compute
import logging


_logger = logging.getLogger(__name__)

class website_sale(openerp.addons.website_sale.controllers.main.website_sale):

    def checkout_values(self, data=None):
        """Overload to add delivery condition"""
        values = super(website_sale, self).checkout_values(data)
        values.update({'delivery_condition' : request.website.sale_get_delivery_condition()})
        #_logger.debug("checkout value end, checkout delivery datetime start : %s", values['checkout']['delivery_datetime_start'])
        return values
    
    @http.route(['/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>',
        '/shop/type/<model("delivery.condition"):condition>', #new shop requests
        '/shop/type/<model("delivery.condition"):condition>/page/<int:page>',
        '/shop/type/<model("delivery.condition"):condition>/category/<model("product.public.category"):category>',
        '/shop/type/<model("delivery.condition"):condition>/category/<model("product.public.category"):category>/page/<int:page>'
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, condition=None, search='', **post):
        """replaced to add current delivery_condition
        TODO: compute values in a dedicated method"""
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        domain = request.website.sale_product_domain(context=context)
        if search:
            for srch in search.split(" "):
                domain += ['|', '|', '|', ('name', 'ilike', srch), ('description', 'ilike', srch),
                    ('description_sale', 'ilike', srch), ('product_variant_ids.default_code', 'ilike', srch)]
        if category:
            domain += [('public_categ_ids', 'child_of', int(category))]
            
        category_obj = pool['product.public.category']
        categ_domain = [('parent_id', '=', False)]
        url = "/shop"
        if condition :
            categs_ids = category_obj.search(cr,uid, 
                            [('condition_id', '=', condition.id)], context=context) 
            #get only products with that delivery condition
                    
            _logger.debug("shop page condition : %d", condition)
            domain += [('public_categ_ids','in',categs_ids)]
            
            categ_domain += [('condition_id', '=', condition.id)]
            url += "/type/%s" % slug(condition)
            #primary categs with that delivery condition
            #todo : assume that child categ have same delivery condition than parent ?
        
        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int,v.split("-")) for v in attrib_list if v]
        attrib_set = set([v[1] for v in attrib_values])

        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domain += [('attribute_line_ids.value_ids', 'in', ids)]
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domain += [('attribute_line_ids.value_ids', 'in', ids)]

        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list)

        if not context.get('pricelist'):
            pricelist = self.get_pricelist()
            context['pricelist'] = int(pricelist)
        else:
            pricelist = pool.get('product.pricelist').browse(cr, uid, context['pricelist'], context)

        product_obj = pool.get('product.template')

        
        product_count = product_obj.search_count(cr, uid, domain, context=context)
        if search:
            post["search"] = search
        if category:
            category = pool['product.public.category'].browse(cr, uid, int(category), context=context)
            url += "/category/%s" % slug(category)
        pager = request.website.pager(url=url, total=product_count, page=page, step=PPG, scope=7, url_args=post)
        product_ids = product_obj.search(cr, uid, domain, limit=PPG, offset=pager['offset'], order='website_published desc, website_sequence desc', context=context)
        products = product_obj.browse(cr, uid, product_ids, context=context)

        style_obj = pool['product.style']
        style_ids = style_obj.search(cr, uid, [], context=context)
        styles = style_obj.browse(cr, uid, style_ids, context=context)

        category_ids = category_obj.search(cr, uid, categ_domain, context=context)
        categs = category_obj.browse(cr, uid, category_ids, context=context)

        attributes_obj = request.registry['product.attribute']
        attributes_ids = attributes_obj.search(cr, uid, [], context=context)
        attributes = attributes_obj.browse(cr, uid, attributes_ids, context=context)

        from_currency = pool.get('product.price.type')._get_field_currency(cr, uid, 'list_price', context)
        to_currency = pricelist.currency_id
        compute_currency = lambda price: pool['res.currency']._compute(cr, uid, from_currency, to_currency, price, context=context)
        
        #
        delivery_condition = request.website.sale_get_delivery_condition()
        
        #
        product_template_objs = self.pool['product.template']
        current_week = product_template_objs.get_current_week(cr, uid, [0], context=None)
         
        
        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'products': products,
            'bins': table_compute().process(products),
            'rows': PPR,
            'styles': styles,
            'categories': categs,
            'attributes': attributes,
            'compute_currency': compute_currency,
            'keep': keep,
            'style_in_product': lambda style, product: style.id in [s.id for s in product.website_style_ids],
            'attrib_encode': lambda attribs: werkzeug.url_encode([('attrib',i) for i in attribs]),
        }
        
        values.update({'delivery_condition' : delivery_condition,#for the description
                       'chosen_condition' : condition}) #for correct links 
        
        values.update({'current_week_number': current_week or None})
        return request.website.render("website_sale.products", values)
    
    
    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        category_obj = pool['product.public.category']
        template_obj = pool['product.template']

        context.update(active_id=product.id)

        if category:
            category = category_obj.browse(cr, uid, int(category), context=context)

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int,v.split("-")) for v in attrib_list if v]
        attrib_set = set([v[1] for v in attrib_values])

        keep = QueryURL('/shop', category=category and category.id, search=search, attrib=attrib_list)

        category_ids = category_obj.search(cr, uid, [], context=context)
        category_list = category_obj.name_get(cr, uid, category_ids, context=context)
        category_list = sorted(category_list, key=lambda category: category[1])

        pricelist = self.get_pricelist()

        from_currency = pool.get('product.price.type')._get_field_currency(cr, uid, 'list_price', context)
        to_currency = pricelist.currency_id
        compute_currency = lambda price: pool['res.currency']._compute(cr, uid, from_currency, to_currency, price, context=context)

        if not context.get('pricelist'):
            context['pricelist'] = int(self.get_pricelist())
            product = template_obj.browse(cr, uid, int(product), context=context)

        #
#         delivery_condition = request.website.sale_get_delivery_condition()
#         template = template_obj.browse(cr, uid, int(product), context=context)
#         public_categ = len(template.public_categ_ids) and template.public_categ_ids[0]
#         #TODO : method sale_order.get_product_cart_compatibility, aussi appeler dans _cart_update ou cart/update pour un avertissement clair
#         
#         product_condition_id = public_categ and public_categ.condition_id and public_categ.condition_id.id
#         
        values = {
            'search': search,
            'category': category,
            'pricelist': pricelist,
            'attrib_values': attrib_values,
            'compute_currency': compute_currency,
            'attrib_set': attrib_set,
            'keep': keep,
            'category_list': category_list,
            'main_object': product,
            'product': product,
            'get_attribute_value_ids': self.get_attribute_value_ids
        }
        values.update({'is_compatible_with_cart' : request.website.sale_is_product_compatible_with_cart(int(product))
                       })
        return request.website.render("website_sale.product", values)
    
    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        _logger.debug("Will test product (ID : %d) compatibility before adding to cart", int(product_id))
        template = request.registry['product.product'].browse(cr,uid, int(product_id), context).product_tmpl_id
        
        if((set_qty > 0 or add_qty > 0) and not request.website.sale_is_product_compatible_with_cart(template.id)) :
            _logger.debug("product not compatible")
            #product = request.registry['product.product'].browse(cr,uid,product_id,context)
            return request.redirect("/shop/product/%s" % slug(template))
        
        #order = request.website.sale_get_order(force_create=1)
        #if(not len(order.website_order_line)):
            #if cart empty, remove the product of the delivery method 
            #(or it will apply its delivery condition to the cart)
            
        #    order.write({'carrier_id': None})
        #    self.pool['sale.order']._delivery_unset(cr, SUPERUSER_ID, [order.id], context=context)
        
        return super(website_sale, self).cart_update(product_id, add_qty, set_qty) 
    #TODO : update website_sale module and modifiy check_carrier to unlink even if compatible but cart cleared
    
    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True)
    def cart_update_json(self, product_id, line_id, add_qty=None, set_qty=None, display=True):
        cr, uid, context = request.cr, request.uid, request.context
        template = request.registry['product.product'].browse(cr,uid, int(product_id), context).product_tmpl_id

        if((set_qty > 0 or add_qty > 0) and not request.website.sale_is_product_compatible_with_cart(template.id)) :
            #product = request.registry['product.product'].browse(cr,uid,product_id,context)
            return request.redirect("/shop/product/%s" % slug(template))
        
        #order = request.website.sale_get_order(force_create=1)
        #if(not len(order.website_order_line)):
            #if cart empty, remove the product of the delivery method 
            #(or it will apply its delivery condition to the cart)
            
        #    order.write({'carrier_id': None})
        #    self.pool['sale.order']._delivery_unset(cr, SUPERUSER_ID, [order.id], context=context)
            
        return super(website_sale, self).cart_update_json(product_id, line_id, add_qty, set_qty,display)
    