# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Delivery Date and Products delays',
    'version': '0.1',
    'category': 'Sales Management', #TODO : e-commerce
    'description': """
    1) Done : Add delivery delay field for every products
    2) TODO : Add categories with special delivery date rules
    2) Done : Add a delivery date field in cart, verify that the difference between current day and delivery date is greater or equal than the maximum product delay of the products in the cart
    3) Done : Add an additionnal requested_delivery_date field to the sales order with the date from the cart form.
===================================================
""",
    'author': 'David Bertha',
    'website': 'http://www..com', #TODO : github
    'depends': ['sale_stock', 'product', 'website_sale_delivery_on_checkout'],
    'data': ['delivery_date_products_view.xml', 'delivery_date_products.xml'],
    'demo': [], #TODO
    'test': [], #TODO
    'installable': True,
    'auto_install': False,
}
