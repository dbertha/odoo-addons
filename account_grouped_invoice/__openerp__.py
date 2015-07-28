# -*- coding: utf-8 -*-
{
    'name': "Grouped Invoice",

    'summary': """
        Extend the flexibility of grouped invoice creation""",

    'description': """
        
    """,

    'author': "David Bertha",
    'website': "",


    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'account', 'sale', 
                'delivery_date' #search based on delivery date TODO : use delivery order
                ], 

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
        'views.xml',
        'report.xml',
        'report_group_invoice.xml'
    ],

    # only loaded in demonstration mode
    'demo': [],
}
