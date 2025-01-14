from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError


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
    product_id = fields.Many2one("product.product", string="Product", related="item_id.product_id", store=True)
    standard_cost = fields.Float(string="Standard Cost")
    quantity = fields.Float(string="Quantity")
    estimated_cost = fields.Float(string="Estimated Cost", compute='_compute_cost',  store=True)
    expense_id = fields.Many2one("hr.expense", string="Expense", readonly=True, ondelete="set null")
    attachment_url = fields.Char("Attachment")
    allow_expense = fields.Boolean('Allow Expense')

    @api.depends('standard_cost', 'quantity')
    def _compute_cost(self):
        for row in self:
            row.estimated_cost = row.standard_cost * row.quantity

    def validate_cost_line(self):
        if self.sale_order_id.state != 'sale':
            raise UserError(_("%s belum di confirm atau SO di locked!" % self.sale_order_id.name))
        if not self.attachment_url:
            raise UserError(_("%s belum belum ada attachment!" % self.name))
        return True

    def create_expense(self):
        employee_id = self.env.user.employee_id
        if employee_id:
            self.validate_cost_line()
            expense_data = {
                'sale_structure_line_id': self.id,
                'product_id': self.product_id.id,
                'name': self.name,
                'unit_amount': self.estimated_cost,
                'employee_id': employee_id.id,
                'payment_mode': 'company_account',
                'reference': self.sale_order_id.name,
                'date': datetime.now().date(),
                'analytic_distribution': {self.sale_order_id.analytic_account_id.id: 100},
            }
            expense_id = self.env['hr.expense'].create(expense_data)
            self.expense_id = expense_id.id
        else:
            raise UserError(_("Only user registered as employee who can create expense!"))
