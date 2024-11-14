# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class CostHeader(models.Model):
    _name = 'agency.cost.header'
    _description = 'Cost Header'
    _inherit = ['mail.thread']

    sequence = fields.Integer("Number", required=True, tracking=True)
    name = fields.Char("Cost Header Name", required=True, tracking=True)
    cost_code_ids = fields.One2many('agency.cost.code', 'cost_header_id', string="Cost Code")
    active = fields.Boolean('Active', default=True, tracking=True)
