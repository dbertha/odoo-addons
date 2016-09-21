{
    'name': 'eCommerce Delivery on Checkout Page',
    'category': 'Website',
    'summary': 'Add Delivery Costs to Online Sales',
    'website': 'https://github.com/dbertha',
    'version': '1.0',
    'description': """
Delivery Costs
==============
WARNING : incompatibility with website_sale_delivery

website_sale_delivery module from OpenERP SA modified to move delivery method choice to checkout page
""",
    'author': 'David Bertha',
    'depends': ['website_sale', 'delivery', 'fonteyne_style', 'delivery_carrier_pickingup'], 
    #fonteyne_style : datetimepicker
    #delivery_picking_up : good template inheritance
    'data': [
        'views/website_sale_delivery_on_checkout.xml',
        'views/website_sale_delivery_on_checkout_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'qweb': [],
    'installable' : False,
}
