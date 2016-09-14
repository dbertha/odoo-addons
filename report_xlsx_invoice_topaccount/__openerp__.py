# -*- coding: utf-8 -*-
# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "Base report xlsx",

    'summary': """
        Inherited module from report_xlsx to create export compatible with topaccount""",
    'author': 'David Bertha,'
              '',
    'website': "https://github.com/dbertha/",
    'category': 'Reporting',
    'version': '1.0',
    'license': 'AGPL-3',
    'data': [
        'report.xml',
    ],
    'depends': [
        'base',
        'report_xlsx'
    ],
}
