# -*- coding: utf-8 -*-

{
    'name': 'Ogone Payment Acquirer : add template param',
    'category': 'Hidden',
    'summary': 'Payment Acquirer: add template URL as parameter with correct shasign',
    'version': '1.0',
    'description': """""",
    'author': 'OpenERP SA',
    'depends': ['payment_ogone'],
    'data': [
        'views/ogone.xml',
        'views/payment_acquirer.xml',
    ],
    'installable' : False,}
