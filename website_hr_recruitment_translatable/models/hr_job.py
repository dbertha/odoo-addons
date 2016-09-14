# -*- coding: utf-8 -*-

from openerp.osv import osv, fields

class hr_job(osv.osv):
    _name = 'hr.job'
    _inherit = 'hr.job'


    _columns = {
        'name': fields.char('Job Name', required=True, select=True, translate=True),
    }
