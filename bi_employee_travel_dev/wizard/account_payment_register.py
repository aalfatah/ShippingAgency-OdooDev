from odoo import _, api, models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def _get_product_advance(self, expense_sheet):
        return self.env.ref("bi_employee_travel_dev.product_emp_advance_upd") \
            if expense_sheet.expense_line_ids.filtered("travel_id") or expense_sheet.expense_line_ids.filtered("travel_expense_id") \
            else self.env.ref("hr_expense_advance_clearing.product_emp_advance", False)
