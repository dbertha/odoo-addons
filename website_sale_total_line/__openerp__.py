{
    'name': 'eCommerce Total Line In Cart',
    'category': 'Website',
    'summary': 'Add a column in cart for the total of the line',
    'website': 'https://github.com/dbertha',
    'version': '1.0',
    'description': """
Total line
==============
This module add a column "total" in the cart, so each line has a total.

""",
    'author': 'David Bertha',
    'depends': ['website_sale'],
    'data': [
        'views/website_sale_total_line.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
}
