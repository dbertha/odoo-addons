# -*- coding: utf-8 -*-
{
    'name': "Groups of portal users",

    'summary': """
        Portal users can be grouped""",

    'description': """
        Portal users are assigned to groups and can be admin of the group.
        The admin access to group related options : remove member, add one,...
    """,

    'author': "David Bertha",
    'website': "",
    'installable' : False,

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'portal', 'portal_sale', 'mail', 
                'website_sale', 'website_sale_delivery_condition',
                'delivery_carrier_pickingup',
                'account_grouped_invoice',
                'delivery_date'], 

    # always loaded
    'data': [
        'data.xml',
        'templates.xml',
        'views.xml',
        'security/ir.model.access.csv',
        'schedular_data.xml'
    ],

    # only loaded in demonstration mode
    'demo': [],
}
