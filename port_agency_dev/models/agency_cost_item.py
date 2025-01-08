# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError


class CostItem(models.Model):
    _name = 'agency.cost.item'
    _description = 'Cost Item'
    _order = 'cost_header_id, sequence'
    _inherit = ['mail.thread']

    sequence = fields.Integer("Number", tracking=True)
    name = fields.Char("Cost Item", required=True, tracking=True)
    code = fields.Char("Cost Code", required=False, tracking=True, copy=False)
    cost_header_id = fields.Many2one('agency.cost.header', "Cost Header", ondelete="cascade")
    active = fields.Boolean('Active', default=True, tracking=True)
    cost_formula = fields.Text(string='Formula', default="result = 1")
    product_id = fields.Many2one('product.product', string="Product", tracking=True)

    _sql_constraints = [
        ('item_name_unique', 'UNIQUE(name)', 'An item name must be unique!'),
    ]

    @api.onchange('code')
    def _onchange_code(self):
        prohibited_chars = "!@#$%^&*()-+=[]{}<>,."
        if self.code:
            for char in self.code:
                if char in prohibited_chars:
                    raise ValidationError(_("Cost item code tidak boleh ada character berikut -> %s." % prohibited_chars))
