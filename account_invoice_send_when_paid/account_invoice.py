# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from openerp import models, fields, api
from openerp import SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)

class account_invoice(models.Model):
    _inherit = 'account.invoice'
    
    @api.multi
    def confirm_paid(self):
        _logger.debug("Will send mail")
        #account_invoice_obj = self.pool.get('account.invoice')
        email_act = self.action_invoice_sent()
        _logger.debug("Will compose mail")
        # send the email
        if email_act and email_act.get('context'):
            composer_obj = self.pool.get('mail.compose.message')
            composer_values = {}
            email_ctx = email_act['context']
            template_values = [
                email_ctx.get('default_template_id'),
                email_ctx.get('default_composition_mode'),
                email_ctx.get('default_model'),
                email_ctx.get('default_res_id'),
            ]
            _logger.debug("before old api 1")
            composer_values.update(composer_obj.onchange_template_id(self._cr, SUPERUSER_ID, None, *template_values, context=self._context).get('value', {}))
            #if not composer_values.get('email_from') and uid == request.website.user_id.id:
            #    composer_values['email_from'] = request.website.user_id.company_id.email
            for key in ['attachment_ids', 'partner_ids']:
                if composer_values.get(key):
                    composer_values[key] = [(6, 0, composer_values[key])]
            _logger.debug("before old api 2")
            composer_id = composer_obj.create(self._cr, SUPERUSER_ID, composer_values, context=email_ctx)
            _logger.debug("before old api 3")
            composer_obj.send_mail(self._cr, SUPERUSER_ID, [composer_id], context=email_ctx)
            _logger.debug("Mail sent : %s", composer_values)
        return super(account_invoice, self).confirm_paid()
