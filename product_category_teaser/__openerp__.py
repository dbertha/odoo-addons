# -*- coding: utf-8 -*-
{
    'name': "Category Teaser on Shop Catalog",

    'summary': """
        Add a description of the product category on the top of the e-shop catalog""",

    'description': """
        Add a description of the product category on the top of the e-shop catalog
    """,

    'author': "David Bertha",
    'website': "",


    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'website', 'website_sale', 'product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
        'views.xml'
    ],

    # only loaded in demonstration mode
    'demo': [],
}
