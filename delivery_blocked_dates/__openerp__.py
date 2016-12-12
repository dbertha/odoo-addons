# -*- coding: utf-8 -*-
{
    'name': "Days and Hours For Delivery Method Availability",

    'summary': """
        Specific blocked dates can be set for either a delivery carrier or a delivery condition or both""",

    'description': """
        Delivery date on checkout website sale can be blocked for specific days, depending either on the delivery condition,
        on the delivery carrier or both
    """,

    'author': "David Bertha",
    'website': "",


    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'website', 'website_sale', 'delivery', 'delivery_date', 'website_sale_delivery_condition'], 
    #delivery_date depends of website_sale_delivery_on_checkout

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'templates.xml',
        #'delivery_report.xml',
        #'report_saleorder_delivery.xml',
        #'report_group_invoice.xml',
        'views.xml'
    ],

    # only loaded in demonstration mode
    'demo': [],
}
