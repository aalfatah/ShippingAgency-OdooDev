# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class CostHeader(models.Model):
    _name = 'agency.cost.header'
    _description = 'Cost Header'

    sequence = fields.Integer("Number", required=True, )
    name = fields.Char("Cost Header Name", required=True, size=64, )
    cost_code_ids = fields.One2many('agency.cost.code', 'cost_header_id', string="Cost Code")
