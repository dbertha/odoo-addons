# -*- coding: utf-8 -*-
{
    'name': "Delivery Condition",

    'summary': """
        Rules for delivery carrier and date based on the products inside the sale order""",

    'description': """
        Public categories are linked to a delivery condition. When a product is added to
        a sale order, the sale order is considered as having that delivery condition.
        Delay rules and delivery carrier are dependant of the delivery condition of the sale order.
    """,

    'author': "David Bertha",
    'website': "",


    'category': 'Sales',
    'version': '0.1',

    'depends': ['base', 'website', 'website_sale', 'product', 'delivery_date_products', 'website_sale_delivery_on_checkout'],

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
