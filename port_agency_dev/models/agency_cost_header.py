# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class CostHeader(models.Model):
    _name = 'agency.cost.header'
    _description = 'Cost Header'
    _inherit = ['mail.thread']

    sequence = fields.Integer("Number", tracking=True)
    name = fields.Char("Cost Header Name", required=True, tracking=True)
    cost_item_ids = fields.One2many('agency.cost.item', 'cost_header_id', string="Cost Item")
    active = fields.Boolean('Active', default=True, tracking=True)
