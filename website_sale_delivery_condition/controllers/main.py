# -*- coding: utf-8 -*-
import werkzeug

from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug
import openerp.addons.website_sale.controllers.main
from openerp.addons.website_sale.controllers.main import QueryURL, PPG, PPR, table_compute
import logging



_logger = logging.getLogger(__name__)

class website_sale(openerp.addons.website_sale.controllers.main.website_sale):
    #TODO : redirect if no delivery condition chosed

    def checkout_values(self, data=None):
        """Overload to add delivery condition"""
        values = super(website_sale, self).checkout_values(data)
        values.update({'delivery_condition' : request.website.sale_get_delivery_condition()})
        #_logger.debug("checkout value end, checkout delivery datetime start : %s", values['checkout']['delivery_datetime_start'])
        return values
    
    @http.route([
        # '/shop',
        # '/shop/page/<int:page>',
        # '/shop/category/<model("product.public.category"):category>',
        # '/shop/category/<model("product.public.category"):category>/page/<int:page>',
        '/shop/type/<model("delivery.condition"):condition>', #new shop requests
        '/shop/type/<model("delivery.condition"):condition>/page/<int:page>',
        '/shop/type/<model("delivery.condition"):condition>/category/<model("product.public.category"):category>',
        '/shop/type/<model("delivery.condition"):condition>/category/<model("product.public.category"):category>/page/<int:page>'
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', ppg=False, condition=None,**post):
        """replaced to add current delivery_condition
        TODO: compute values in a dedicated method"""
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        #showing the page considered as choosing a delivery condition
        if condition : 
            order = request.website.sale_get_order(force_create=1, context=context)
            if order.delivery_condition.id != condition.id and order.order_line :
                #reset cart because another condition has been chosen
                for line in order.order_line :
                    line.unlink()

            order.delivery_condition = condition
        else :
            if request.website.delivery_condition_url :
                return request.redirect(request.website.delivery_condition_url)

        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attributes_ids = set([v[0] for v in attrib_values])
        attrib_set = set([v[1] for v in attrib_values])

        domain = self._get_search_domain(search, category, attrib_values)

        keep = QueryURL('/shop', category=category and int(category),condition=condition and int(condition), search=search, attrib=attrib_list)




        if not context.get('pricelist'):
            pricelist = self.get_pricelist()
            context['pricelist'] = int(pricelist)
        else:
            pricelist = pool.get('product.pricelist').browse(cr, uid, context['pricelist'], context)
        

        url = "/shop"
        if search:
            post["search"] = search
        if condition :
            if request.env.user.enterprise_portal and not condition.enterprise_portal_published :
                return request.redirect("/")
            url += "/type/%s" % slug(condition)
        if category:
            category = pool['product.public.category'].browse(cr, uid, int(category), context=context)
            url += "/category/%s" % slug(category)
        if attrib_list:
            post['attrib'] = attrib_list


        style_obj = pool['product.style']
        style_ids = style_obj.search(cr, uid, [], context=context)
        styles = style_obj.browse(cr, uid, style_ids, context=context)

        category_obj = pool['product.public.category']
        category_domain = [('parent_id', '=', False)]
        if condition :
            category_domain = ['&'] + category_domain + [('condition_id', '=', condition.id)]
        category_ids = category_obj.search(cr, uid, category_domain, context=context)
        categs = category_obj.browse(cr, uid, category_ids, context=context)

        product_obj = pool.get('product.template')

        parent_category_ids = []
        if category:
            parent_category_ids = [category.id]
            current_category = category
            while current_category.parent_id:
                parent_category_ids.append(current_category.parent_id.id)
                current_category = current_category.parent_id

        product_count = product_obj.search_count(cr, uid, domain, context=context)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        product_ids = product_obj.search(cr, uid, domain, limit=ppg, offset=pager['offset'], order=self._get_search_order(post), context=context)
        products = product_obj.browse(cr, uid, product_ids, context=context)

        attributes_obj = request.registry['product.attribute']
        if product_ids:
            attributes_ids = attributes_obj.search(cr, uid, [('attribute_line_ids.product_tmpl_id', 'in', product_ids)], context=context)
        attributes = attributes_obj.browse(cr, uid, attributes_ids, context=context)

        from_currency = pool['res.users'].browse(cr, uid, uid, context=context).company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = lambda price: pool['res.currency']._compute(cr, uid, from_currency, to_currency, price, context=context)


        



        delivery_condition = request.website.sale_get_delivery_condition()

        product_template_objs = request.env['product.template']
        current_week = product_template_objs.get_current_week()
         

        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'products': products,
            'bins': table_compute().process(products, ppg),
            'rows': PPR,
            'styles': styles,
            'categories': categs,

            'chosen_condition' : condition,
            'delivery_condition' : delivery_condition,
            'current_week_number': current_week or None,

            'attributes': attributes,
            'compute_currency': compute_currency,
            'keep': keep,
            'parent_category_ids': parent_category_ids,
            'style_in_product': lambda style, product: style.id in [s.id for s in product.website_style_ids],
            'attrib_encode': lambda attribs: werkzeug.url_encode([('attrib',i) for i in attribs]),
        }
        if category:
            values['main_object'] = category
        return request.website.render("website_sale.products", values)

        
            #primary categs with that delivery condition
            #todo : assume that child categ have same delivery condition than parent ?
        
        
        
        
        
    
    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        category_obj = pool['product.public.category']
        template_obj = pool['product.template']

        context.update(active_id=product.id)

        if category:
            category = category_obj.browse(cr, uid, int(category), context=context)
            category = category if category.exists() else False

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int,v.split("-")) for v in attrib_list if v]
        attrib_set = set([v[1] for v in attrib_values])

        keep = QueryURL('/shop', category=category and category.id, search=search, attrib=attrib_list)

        category_ids = category_obj.search(cr, uid, [('parent_id', '=', False)], context=context)
        categs = category_obj.browse(cr, uid, category_ids, context=context)

        pricelist = self.get_pricelist()

        from_currency = pool['res.users'].browse(cr, uid, uid, context=context).company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = lambda price: pool['res.currency']._compute(cr, uid, from_currency, to_currency, price, context=context)

        # get the rating attached to a mail.message, and the rating stats of the product
        Rating = pool['rating.rating']
        rating_ids = Rating.search(cr, uid, [('message_id', 'in', product.website_message_ids.ids)], context=context)
        ratings = Rating.browse(cr, uid, rating_ids, context=context)
        rating_message_values = dict([(record.message_id.id, record.rating) for record in ratings])
        rating_product = product.rating_get_stats([('website_published', '=', True)])

        if not context.get('pricelist'):
            context['pricelist'] = int(self.get_pricelist())
            product = template_obj.browse(cr, uid, int(product), context=context)

        values = {
            'search': search,
            'category': category,
            'pricelist': pricelist,
            'attrib_values': attrib_values,
            'compute_currency': compute_currency,
            'attrib_set': attrib_set,
            'keep': keep,
            'categories': categs,
            'main_object': product,
            'product': product,
            'get_attribute_value_ids': self.get_attribute_value_ids,
            'rating_message_values' : rating_message_values,
            'rating_product' : rating_product,

            'chosen_condition' : request.website.sale_get_delivery_condition(),
            'is_compatible_with_cart' : request.website.sale_is_product_compatible_with_cart(int(product))
                       
        }
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
        
        context = dict(request.env.context)
        context['update_not_json'] = True
        request.env.context = context
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
    



    # @http.route(['/shop/payment/transaction/<int:acquirer_id>'], type='json', auth="public", website=True)
    # def payment_transaction(self, acquirer_id):
    #     if request.env.user.enterprise_portal and \
    #         not (request.env['payment.acquirer'].browse(acquirer_id).auto_confirm == 'at_pay_now') :
    #         #send mail even if not confirmed
    #         order = request.website.sale_get_order()
    #         order.is_enterprise_portal = True
    #         order.force_quotation_send()
    #     return super(website_sale, self).payment_transaction(acquirer_id)


    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True)
    def confirm_order(self, **post):
        order = request.website.sale_get_order(context=request.context)
        res = super(website_sale, self).confirm_order(**post)
        # _logger.debug(res)
        # _logger.debug(res.headers and res.headers.get('location'))
        if request.env.user.enterprise_portal and "payment" in (res.headers and res.headers.get('location', '') or '') :
            #avoid payment page and send mail for quotation
            order.is_enterprise_portal = True
            order.force_quotation_send()
            request.website.sale_reset(context=request.context)
            return request.redirect('/shop/confirmation')
        return res


    @http.route('/shop/payment/get_status/<int:sale_order_id>', type='json', auth="public", website=True)
    def payment_get_status(self, sale_order_id, **post):
        cr, uid, context = request.cr, request.uid, request.context

        res = super(website_sale, self).payment_get_status(sale_order_id,**post)
        if request.env.user.enterprise_portal :
            values = {}
        
            values.update({'tx_ids': False, 'state': 'done', 'validation': None})
            
            return res.update({'message': request.website._render("website_sale.order_state_message", values)})
        return res