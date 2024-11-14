from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp


class bill_quantity_line_manpower(models.Model):
    _name = 'bill.quantity.line.manpower'
    _description = 'Bill Of Quantity Manpower'

    boq_line_id = fields.Many2one('bill.quantity.line', 'Manpower', ondelete='cascade')
    cost_code_id = fields.Many2one('cost.code', 'Cost Code', ondelete='restrict')
    name = fields.Char('Description', related='cost_code_id.description', store=True)
    amount_select = fields.Selection([
        ('entry', 'Entry Amount'),
        ('fix', 'Fixed Amount'),
        ('code', 'Python Code'),
    ], string='Amount Type', index=True, related='cost_code_id.amount_select', store=True)
    cost_header_id = fields.Many2one('cost.header', 'Cost Header', ondelete='restrict', related='cost_code_id.cost_header_id', store=True)
    amount = fields.Float('Amount', digits='Account')