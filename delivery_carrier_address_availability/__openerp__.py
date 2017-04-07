# -*- coding: utf-8 -*-
{
    'name': "Delivery Method Available to some Addresses",

    'summary': """
        Ease the destination configuration for delivery methods""",

    'description': """
        Delivery method with destination configuration are available for public user (even if they doesn't have a zipcode encoded yet),
        destination check is made after checkout.
        Zipcodes are list instead of range 
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
        #'delivery_report.xml',
        #'report_saleorder_delivery.xml',
        #'report_group_invoice.xml',
        'views.xml'
    ],

    # only loaded in demonstration mode
    'demo': [],
}
