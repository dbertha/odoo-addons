# -*- coding: utf-8 -*-
{
    'name': "Delivery Condition",

    'summary': """
        Rules for delivery carrier and date based on the products inside the sale order""",

    'description': """
        Public categories are linked to a delivery condition. When a webshop is chosen, the sale order is considered as having that delivery condition.
        Delay rules and delivery carrier are dependent of the delivery condition of the sale order.
    """,

    'author': "David Bertha",
    'website': "",
    'installable' : True,

    'category': 'Sales',
    'version': '0.1',

    'depends': ['base', 'website', 'website_sale',
                 'website_sale_rotating', #to add number of week in shop page rendering
                'product', 'delivery_date', 'website_sale_delivery_on_checkout'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'res_config_view.xml',
        'views.xml',
        'templates.xml'
    ],

    # only loaded in demonstration mode
    'demo': [],
}
