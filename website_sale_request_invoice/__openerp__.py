# -*- coding: utf-8 -*-
{
    'name': "Optionnal Invoice send to partner",

    'summary': """
        Add a check box on checkout page for invoice by mail acceptance""",

    'description': """
        Add a boolean field in partner, this field is checked in invoice mail template (default partner_to value)
        You should manually add ${object.partner_id.accept_invoice and object.partner_id.id or ''} instead of ${object.partner_id.id}
        in the template mail configuration.
    """,

    'author': "David Bertha",
    'website': "www.github.com/dbertha",
    'installable' : False,

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'website', 'website_sale', 'account',
                'website_sale_autopay', #auto link ecommerce transaction to invoice
                'account_invoice_send_when_paid'], #auto send invoice default template when paid

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
        'views.xml'
    ],

    # only loaded in demonstration mode
    'demo': [],
}
