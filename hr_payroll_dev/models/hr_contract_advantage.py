# -*- coding:utf-8 -*-

from odoo import api, fields, models


class HrContractAdvantage(models.Model):
    _name = 'hr.contract.advantage'
    _description = "Employee's Advantage on Contract"
    _order = 'sequence'

    sequence = fields.Integer(required=True, index=True, related='advantage_id.sequence', store=True)
    contract_id = fields.Many2one('hr.contract', required=True)
    advantage_id = fields.Many2one('hr.contract.advantage.template', required=True)
    code = fields.Char('Code', related='advantage_id.code')
    currency_id = fields.Many2one('res.currency', 'Currency', related='contract_id.currency_id')
    value = fields.Monetary('Value')

    _sql_constraints = [
        ('advantage_uniq', 'unique (contract_id, advantage_id)', 'Advantage already exists!'),
    ]
