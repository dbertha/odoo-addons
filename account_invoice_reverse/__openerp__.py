# -*- coding: utf-8 -*-
{
    'name': "Reverse Invoice for independant shops",

    'summary': """
        Generate supplier invoice from the sales made for another shop""",

    'description': """
        Cron method to generate a custom invoice report of supplier invoice.
        The delivery methods that are pickup and related to a partner that is a company 
        will receive by mail an invoice for all sales made for them.
    """,

    'author': "David Bertha",
    'website': "",
    'installable' : False,

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'website', 'website_sale', 'delivery', 'delivery_carrier_pickingup',
                'account_grouped_invoice'], 

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
        'views.xml',
        'schedular_data.xml'
    ],

    # only loaded in demonstration mode
    'demo': [],
}
