# -*- coding: utf-8 -*-
{
    'name': "Minimum Amount For Delivery Method",

    'summary': """
        Add a minimum amount field in delivery method""",

    'description': """
        Delivery method won't be available if the total amount of the sale order
        is lower than the minimum amount for the delivery method
    """,

    'author': "David Bertha",
    'website': "",
    'installable' : True,

    'category': 'Uncategorized',
    'version': '2',

    'depends': ['base', 'website', 'website_sale', 'delivery'], 

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
