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
    'name': 'Delivery Date In Sale Order',
    'version': '0.1',
    'category': 'Sales Management', #TODO : e-commerce
    'description': """
    Add an additional requested_delivery_date field to the sales order 
    with the date from the cart (checkout form).
===================================================
""",
    'author': 'David Bertha',
    'website': 'http://www.github.com/dbertha',
    'depends': ['sale_stock', 'product', 'website_sale', 'website_sale_delivery_on_checkout', 'fonteyne_style'],
    #fonteyne_style : datetimepicker, moment.js (2.9)
    'data': ['delivery_date_view.xml', 'delivery_date.xml'],
    'demo': [], #TODO
    'test': [], #TODO
    'installable': True,
    'auto_install': False,
}
