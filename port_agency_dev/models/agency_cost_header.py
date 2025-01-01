# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class CostHeader(models.Model):
    _name = 'agency.cost.header'
    _description = 'Cost Header'
    _inherit = ['mail.thread']

    sequence = fields.Integer("Number", tracking=True)
    name = fields.Char("Header Name", required=True, tracking=True)
    desc = fields.Char("Description", tracking=True)
    route = fields.Char("Route", tracking=True)
    cost_item_ids = fields.One2many('agency.cost.item', 'cost_header_id', string="Cost Item", copy=True)
    active = fields.Boolean('Active', default=True, tracking=True)
