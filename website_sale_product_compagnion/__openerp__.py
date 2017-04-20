# -*- coding: utf-8 -*-
{
    'name': "Products compagnions",

    'summary': 
    """Rules to add some products to cart if another product is present""",

    'description': 
    """Rules based on quantity to propose some packs to be chosen by the customer.
    If only one pack, this can be used as a mandatory compagnion.
    Can be used for mandatory warranty, cash security, ...""",

    'author': "David Bertha",
    'website': "",
    'installable' : False,

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

#TODO :
# sale_order.check_mandatory_products() : if false, still need to add products
# product_product field : many2many compagnion_rules
# product_compagnion_rule : fields quantity lower, quantity upper, many2many compagnion_packs
# product_compagnion_pack : fields quantity_to_add, many2one product_to_add
# sale_order.get_packs() : return (line.id : [packs_to_choose])
# sale_order_line.get_packs() : [packs_to_choose based on quantity and product.compagnion_rules]
# checkout_redirection : if sale_order.check_mandatory_products(), redirect to compagnion page
# validate cart should redirect to compagnion page. 
#Compagnion redirection redirect to checkout if sale_order.has_accompagnied_lines() if False