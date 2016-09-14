# -*- coding: utf-'8' "-*-"

from hashlib import sha1
import logging
from lxml import etree, objectify
from pprint import pformat
import time
from datetime import datetime
from urllib import urlencode
import urllib2
import urlparse

from openerp.addons.payment.models.payment_acquirer import ValidationError
from openerp.addons.payment_ogone.controllers.main import OgoneController
from openerp.addons.payment_ogone.data import ogone
from openerp.osv import osv, fields
from openerp.tools import float_round, DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.float_utils import float_compare, float_repr

_logger = logging.getLogger(__name__)


class PaymentAcquirerOgone(osv.Model):
    _inherit = 'payment.acquirer'


    _columns = {
        'ogone_template': fields.char('Dynamic template URL if needed', required_if_provider='ogone'),
    }



    def ogone_form_generate_values(self, cr, uid, id, partner_values, tx_values, context=None):
        base_url = self.pool['ir.config_parameter'].get_param(cr, uid, 'web.base.url')
        acquirer = self.browse(cr, uid, id, context=context)
        ogone_tx_values = dict(tx_values)
        temp_ogone_tx_values = {
            'PSPID': acquirer.ogone_pspid,
            'ORDERID': tx_values['reference'],
            'AMOUNT': float_repr(float_round(tx_values['amount'], 2) * 100, 0),
            'CURRENCY': tx_values['currency'] and tx_values['currency'].name or '',
            'LANGUAGE':  partner_values['lang'],
            'CN':  partner_values['name'],
            'EMAIL':  partner_values['email'],
            'OWNERZIP':  partner_values['zip'],
            'OWNERADDRESS':  partner_values['address'],
            'OWNERTOWN':  partner_values['city'],
            'OWNERCTY':  partner_values['country'] and partner_values['country'].code or '',
            'OWNERTELNO': partner_values['phone'],
            'ACCEPTURL': '%s' % urlparse.urljoin(base_url, OgoneController._accept_url),
            'DECLINEURL': '%s' % urlparse.urljoin(base_url, OgoneController._decline_url),
            'EXCEPTIONURL': '%s' % urlparse.urljoin(base_url, OgoneController._exception_url),
            'CANCELURL': '%s' % urlparse.urljoin(base_url, OgoneController._cancel_url),
        }
        #add template parameter #TODO : inheritance way
        if acquirer.ogone_template :
            temp_ogone_tx_values['TP'] = acquirer.ogone_template
        if ogone_tx_values.get('return_url'):
            temp_ogone_tx_values['PARAMPLUS'] = 'return_url=%s' % ogone_tx_values.pop('return_url')
        shasign = self._ogone_generate_shasign(acquirer, 'in', temp_ogone_tx_values)
        temp_ogone_tx_values['SHASIGN'] = shasign
        ogone_tx_values.update(temp_ogone_tx_values)
        return partner_values, ogone_tx_values