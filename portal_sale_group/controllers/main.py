# -*- coding: utf-8 -*-
import werkzeug

from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug
from openerp.addons.web.controllers.main import login_redirect
import openerp.addons.delivery_date.controllers.main
from datetime import date, datetime, timedelta, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
import pytz
import logging

_logger = logging.getLogger(__name__)

class WebsiteSale(openerp.addons.delivery_date.controllers.main.website_sale):

    def checkout_values(self, data=None):
        """overload to add group delivery address = administrator address"""
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        
        values = super(WebsiteSale, self).checkout_values(data)
        _logger.debug("checkout value overload for delivery grouped shipping address")
        order = request.website.sale_get_order(force_create=1, context=context) 
        values.update({'group_partner' : order.portal_group_id and order.portal_group_id.administrator.partner_id})
        return values
    
    def checkout_redirection(self, order):
        """Overload to check if user have sufficient money from its group"""
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        redirection = super(WebsiteSale, self).checkout_redirection(order)
        if not redirection and order.portal_group_id :
            user = registry.get('res.users').browse(cr, SUPERUSER_ID, uid, context=context)
            if order.amount_total > user.available_amount :
                return request.redirect("/cart")
        return redirection
    
    @http.route(['/shop/cart'], type='http', auth="public", website=True)
    def cart(self, **post):
        """Overload to handle when cart amount if over user available amount"""
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        res = super(WebsiteSale, self).cart(**post)
        order = res.qcontext['order'] #TODO : qweb template doesn't use this value, so we shouldn't rely on it
        if order and order.portal_group_id :
            user = registry.get('res.users').browse(cr, SUPERUSER_ID, uid, context=context)
            res.qcontext['user_available_amount'] = user.available_amount
        return res

    
    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True)
    def confirm_order(self, **post):
        """Overload because no payment should be proposed for group order, 
        invoice should be periodically send to the administrator
        Rewrite all the function because there is no hookpoint"""
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        context.update({'checkout' : False})
        order = request.website.sale_get_order(context=context)
        
        if not order:
            return request.redirect("/shop")
        carrier_id = order.carrier_id.id
        
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection
        
        if order.portal_group_id :

            values = self.checkout_values(post)
    
            values["error"] = self.checkout_form_validate(values["checkout"])
            if values["error"]:
                #need delivery informations
                sale_order_obj = request.registry.get('sale.order')
                values.update(sale_order_obj._get_website_data(cr, uid, order, context))
                return request.website.render("website_sale.checkout", values)
    
            self.checkout_form_save(values["checkout"])
    
            
    
            order = request.website.sale_get_order(update_pricelist=True, context=context)
            sale_order_obj = request.registry.get('sale.order')
            if not request.registry['sale.order']._check_carrier_quotation(cr, uid, order, force_carrier_id=carrier_id, context=context) :
                _logger.debug("Delivery carrier has changed, send error to qweb")
                
                #need delivery informations
                
                context.update({'checkout' : True})
                values.update(sale_order_obj._get_website_data(cr, uid, order, context))
                values.update(self.checkout_values()) #update carrier info
                values["error"].update({'delivery_zip' : 'not_available'})
                return request.website.render("website_sale.checkout", values)
            _logger.debug("Before confirmation")
            request.session['sale_last_order_id'] = order.id
            #context=dict(context or {},send_email = True)
            registry.get('sale.order').action_button_confirm(cr, uid, order.id, context=context)
            
            #old odoo version doesn't send mail with action_button_confirm
            order_id = order.id
            email_act = sale_order_obj.action_quotation_send(cr, SUPERUSER_ID, [order_id], context=context)
            if email_act and email_act.get('context'):
                composer_obj = registry['mail.compose.message']
                composer_values = {}
                email_ctx = email_act['context']
                template_values = [
                    email_ctx.get('default_template_id'),
                    email_ctx.get('default_composition_mode'),
                    email_ctx.get('default_model'),
                    email_ctx.get('default_res_id'),
                ]
                composer_values.update(composer_obj.onchange_template_id(cr, SUPERUSER_ID, None, *template_values, context=context).get('value', {}))
                if not composer_values.get('email_from'):
                    composer_values['email_from'] = sale_order_obj.browse(cr, uid, order_id, context=context).company_id.email
                for key in ['attachment_ids', 'partner_ids']:
                    if composer_values.get(key):
                        _logger.debug("Composer values : %s : %s", key, composer_values[key])
                        composer_values[key] = [(6, 0, composer_values[key])]
                composer_id = composer_obj.create(cr, SUPERUSER_ID, composer_values, context=email_ctx)
                _logger.debug("After create")
                composer_obj.send_mail(cr, SUPERUSER_ID, [composer_id], context=email_ctx)
                _logger.debug("After send_mail")
            
            #order.with_context(dict(context, send_email=True)).action_button_confirm(cr, uid, order.id) #new api way
            #uid should be portal user
            
            #no need to go further
            # clean context and session, then redirect to the confirmation page
            request.website.sale_reset(context=context)

            return request.redirect('/shop/confirmation')
        
        return super(WebsiteSale,self).confirm_order(**post)
    
    
    @http.route('/shop/payment/get_status/<int:sale_order_id>', type='json', auth="public", website=True)
    def payment_get_status(self, sale_order_id, **post) :
        cr, uid, context = request.cr, request.uid, request.context

        order = request.registry['sale.order'].browse(cr, SUPERUSER_ID, sale_order_id, context=context)
        assert order.id == request.session.get('sale_last_order_id')
        if order and order.is_portal_order() :
            return {
            'state': 'recorded',
            'message': '<p>%s</p>' % _('Your group order has been received.'),
            'validation': None
        }
        return super(WebsiteSale,self).payment_get_status(sale_order_id,**post)
    
    def _parse_delivery_date(self, data) :
        """Add group hour to delivery date"""
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        delivery_date_set = super(WebsiteSale, self)._parse_delivery_date(data)
        user = registry.get('res.users').browse(cr, SUPERUSER_ID, uid, context=context)
        delivery_datetime_start = delivery_date_set.get('delivery_datetime_start', False)
        _logger.debug("Delivery date parsing with User name %s", user.name)
        if delivery_datetime_start and user.portal_group_id :
            time_delta = delivery_date_set.get('delivery_datetime_end') - delivery_datetime_start
            tzone = timezone('Europe/Brussels')
            delivery_date = delivery_datetime_start.astimezone(tzone).date()
            delivery_time = time(user.portal_group_id.hour_of_delivery, 0)
            delivery_date_set['delivery_datetime_start'] = tzone.localize(datetime.combine(delivery_date, delivery_time)).astimezone(pytz.utc)
            delivery_date_set['delivery_datetime_end'] = delivery_date_set['delivery_datetime_start'] + time_delta
            _logger.debug("Delivery date parsing new datetime %s", delivery_date_set['delivery_datetime_start'])
        return delivery_date_set