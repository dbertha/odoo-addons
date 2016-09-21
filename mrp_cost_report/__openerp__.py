# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'MRP bom cost upgrade',
    'version': '1.1',
    'category': 'Manufacturing',
    'sequence': 14,
    'depends': ['mrp', 'report'],
    'description': """
Upgrade Bom cost report with work center infos and custom fields
    """,
    'data': [

        #'views/report_mrpbomcost.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
