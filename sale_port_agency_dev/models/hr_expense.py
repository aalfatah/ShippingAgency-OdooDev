from odoo import models, fields, api, _


class Expense(models.Model):
    _inherit = 'hr.expense'

    sale_structure_line_id = fields.Many2one("sale.cost.structure.line", "Structure Line", readonly=True,
                                             ondelete="restrict")
    attachment_url = fields.Char("Attachment", related="sale_structure_line_id.attachment_url")
