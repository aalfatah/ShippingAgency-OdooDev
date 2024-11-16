# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp


class CostItem(models.Model):
    _name = 'agency.cost.item'
    _description = 'Cost Item'
    _inherit = ['mail.thread']

    sequence = fields.Integer("Number", tracking=True)
    name = fields.Char("Cost Item", required=True, tracking=True)
    code = fields.Char("Cost Code", required=True, tracking=True)
    cost_header_id = fields.Many2one('agency.cost.header', "Cost Header", ondelete="cascade")
    active = fields.Boolean('Active', default=True, tracking=True)
    cost_formula = fields.Text(string='Formula', default="result = 1")
