# -*- coding: utf-8 -*-
{
    'name': "Fonteyne Style",
    'category': 'Theme',
    'version': '1.0',

    'summary': """
        CSS and JS for Fonteyne""",

    'description': """
        Add some CSS ans JS features
    """,


    'author': "Six vallées",
    'website': "http://sixvallees.com",

    'installable' : False,
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website', 'website_sale','payment_ogone'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/templates.xml',
        #'views/options.xml',
        'views/snippets.xml',
        'views/layout.xml',
        'views/tracking.xml',
        'views/contact.xml',
    ],


    # Technical options
    'demo': [],
    'test': [],
    'installable': True,
    # 'auto_install':False,
    # 'active':True,

}
