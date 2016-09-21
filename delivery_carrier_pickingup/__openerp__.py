# -*- coding: utf-8 -*-
{
    'name': "Picking Address with Delivery Method",

    'summary': """
        Add a partner field in delivery method""",

    'description': """
        Add a partner field in delivery method. The address of the partner
        will be used as shipping address on webshop
    """,

    'author': "David Bertha",
    'website': "",
    'installable' : False,

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'website', 'website_sale'], 

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
        'delivery_report.xml',
        'report_saleorder_delivery.xml',
        'views.xml'
    ],

    # only loaded in demonstration mode
    'demo': [],
}
