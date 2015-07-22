# -*- coding: utf-8 -*-
{
    'name': "Days and Hours For Delivery Method Availability",

    'summary': """
        Delivery method can receive specific delivery periods""",

    'description': """
        Delivery method chosen in checkout will constraint delivery date to be in
        its allowed time intervals.
        Time intervals (like opening hours) can be specified for each day of the week.
        Unavailable days can be translated as an available period of 0 minutes for that day
    """,

    'author': "David Bertha",
    'website': "",


    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'website', 'website_sale', 'delivery', 'delivery_date'], 
    #delivery_date depends of website_sale_delivery_on_checkout

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        #'templates.xml',
        #'delivery_report.xml',
        #'report_saleorder_delivery.xml',
        #'report_group_invoice.xml',
        'views.xml'
    ],

    # only loaded in demonstration mode
    'demo': [],
}
