# -*- coding: utf-8 -*-
{
    'name': "Picking Address with Delivery Method",

    'summary': """
        Add a stock location field in delivery method""",

    'description': """
        Add a stock location field in delivery method. The partner of the location
        will be used as shipping address on webshop when this carrier is chosen
    """,

    'author': "David Bertha",
    'website': "",
    'installable' : True,

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'website', 'website_sale', 'delivery'], 

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
        # 'delivery_report.xml',
        # 'report_saleorder_delivery.xml',
        'views.xml'
    ],

    # only loaded in demonstration mode
    'demo': [],
}
