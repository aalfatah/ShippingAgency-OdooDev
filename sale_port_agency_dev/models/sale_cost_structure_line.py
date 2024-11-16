from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class SaleCostStructureLine(models.Model):
    _name = 'sale.cost.structure.line'
    _description = 'Sale Cost Structure Line'
    _inherit = ['mail.thread']

    sequence = fields.Integer("Number")
    name = fields.Text(string="Description", required=True)
    display_type = fields.Selection([('line_section', "Section"), ('line_note', "Note")], default=False)
    cost_structure_id = fields.Many2one('agency.cost.structure', string="Cost Structure", ondelete='restrict')
    sale_order_id = fields.Many2one('sale.order', string="Sales Order", ondelete='cascade')
    sale_order_line_id = fields.Many2one('sale.order.line', string="Sales Line", ondelete='cascade')
    package_id = fields.Many2one('agency.cost.package', string="Package")
    header_id = fields.Many2one('agency.cost.header', string="Header")
    item_id = fields.Many2one('agency.cost.item', string="Item")
    code = fields.Char("Cost Code", related="item_id.code")
    estimated_cost = fields.Float(string="Estimated Cost")
