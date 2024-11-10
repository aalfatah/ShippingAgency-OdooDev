from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class ExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    is_travel = fields.Boolean('is a travel', compute='_check_travel')

    def _check_travel(self):
        for sheet in self:
            sheet.is_travel = self.expense_line_ids.filtered(lambda rec: rec.travel_id or rec.travel_expense_id).exists()

    def unlink(self):
        for sheet in self:
            travel = self.env['travel.request'].sudo().search([('name', '=', sheet.name)])
            if travel:
                travel.state = 'returned'
        super(ExpenseSheet, self).unlink()

    # def _get_product_advance(self):
    #     return self.env.ref("bi_employee_travel_dev.product_emp_advance_upd") \
    #         if self.expense_line_ids.filtered("travel_id") or self.expense_line_ids.filtered("travel_expense_id") \
    #         else self.env.ref("hr_expense_advance_clearing.product_emp_advance", False)


class ExpenseTravel(models.Model):
    _inherit = 'hr.expense'

    number = fields.Char(related="sheet_id.number", string="Number")
    travel_id = fields.Many2one('travel.request', ondelete="cascade")
    travel_expense_id = fields.Many2one('travel.request', ondelete="cascade")

    def action_submit_expenses(self):
        res = super(ExpenseTravel, self).action_submit_expenses()
        # if res.get('context'):
        #     res.get('context').update({'default_payment_mode': self.payment_mode,
        #                                'default_payslip_date': self.payslip_date})
        for exp in self:
            if not exp.advance:
                sheet = self.env['hr.expense.sheet'].search([('name', '=', exp.name), ('advance', '=', True), ('clearing_residual', '>', 0)], limit=1)
                if sheet:
                    exp.sheet_id.advance_sheet_id = sheet.id

                    travel = self.env['travel.request'].sudo().search([('name', '=', exp.name)])
                    if travel:
                        if not travel.expense_sheet_id:
                            travel.expense_sheet_id = exp.sheet_id.id
                        if travel.state == 'returned':
                            travel.write({'state': 'submitted'})
        return res

    def unlink(self):
        for row in self:
            if row.state not in 'draft,refused' or row.sheet_id:
                raise UserError(_('You can not delete an expense where state not in draft or refused or already has sheet.'))
            super(ExpenseTravel, row).unlink()

    # def _get_product_advance(self):
    #     return self.env.ref("bi_employee_travel_dev.product_emp_advance_upd") \
    #         if self.filtered("travel_id") or self.filtered("travel_expense_id") \
    #         else self.env.ref("hr_expense_advance_clearing.product_emp_advance", False)
