# -*- coding: utf-8 -*-
{
    'name': "Fonteyne Style",

    'summary': """
        CSS and JS for Fonteyne""",

    'description': """
        Add some CSS ans JS features
    """,

    'author': "Your Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
    ],

    # only loaded in demonstration mode
    'demo': [],
}
