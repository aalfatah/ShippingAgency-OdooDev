# -*- coding:utf-8 -*-
import json

from odoo import api, fields, models
import json


class HrContract(models.Model):
    _inherit = 'hr.contract'

    advantage_ids = fields.One2many('hr.contract.advantage', 'contract_id', string='Advantage', tracking=True)

    def advantage_amount(self, code):
        self.ensure_one()
        return self.advantage_ids.filtered(lambda a: a.code == code).value
