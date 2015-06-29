# -*- coding: utf-8 -*-
{
    'name': "Rotating products available on shop",

    'summary': """
        Products publication cycling on weeks""",

    'description': """
        Products can be marked with a week number and displayed on e-shop only when
        current week is that number. That number is cycling.
    """,

    'author': "David Bertha",
    'website': "",


    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'website', 'website_sale', 'product', 'delivery_date_products', 'website_sale_delivery_on_checkout'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        'res_config_view.xml',
        'views.xml',
        'templates.xml'
    ],

    # only loaded in demonstration mode
    'demo': [],
}
