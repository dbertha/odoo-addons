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
    'name': 'Deivery : move choices from paiement page to checkout page',
    'version': '0.1',
    'category': 'Website', 
    'description': """
    Move delivery method and date choice to checkout page
""",
    'author': 'David Bertha',
    'website': 'https://github.com/dbertha', 
    'depends': ['sale_stock', 'website_sale_delivery', 'delivery_date_products'],
    'data': ['delivery_move_paiement_to_checkout.xml'],
    'demo': [], 
    'test': [], 
    'installable': True,
    'auto_install': False,
}
