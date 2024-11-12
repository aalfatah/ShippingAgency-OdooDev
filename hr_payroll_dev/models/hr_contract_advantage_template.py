# -*- coding:utf-8 -*-

from odoo import api, fields, models


class HrContractAdvandageTemplate(models.Model):
    _inherit = 'hr.contract.advantage.template'
    _order = 'sequence'

    sequence = fields.Integer(required=True, index=True, default=5, help='Use to arrange calculation sequence')
