# -*- coding: utf-8 -*-
{
    'name': "Products automatically added with other products",

    'summary': 
    """When a product is added to the cart, its associated products are automatically added""",

    'description': 
    """Can be used for mandatory warranty, cash security, ...""",

    'author': "David Bertha",
    'website': "",


    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'website', 'website_sale', 'product', 'website_sale_delivery_condition'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
        'views.xml'
    ],

    # only loaded in demonstration mode
    'demo': [],
}
