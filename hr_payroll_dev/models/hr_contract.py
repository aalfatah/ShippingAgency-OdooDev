# -*- coding:utf-8 -*-

from odoo import api, fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    advantage_ids = fields.One2many('hr.contract.advantage', 'contract_id', string='Advantage')

    def advantage_amont(self, code):
        self.ensure_one()
        return self.advantage_ids.filtered(lambda a: a.code == code).value
