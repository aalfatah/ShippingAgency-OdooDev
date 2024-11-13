# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp


class CostCode(models.Model):
    _name = 'agency.cost.code'
    _description = 'Cost Code'

    sequence = fields.Integer("Number", required=True, )
    name = fields.Char("Cost Code", required=True, )
    cost_header_id = fields.Many2one('agency.cost.header', "Cost Header")
