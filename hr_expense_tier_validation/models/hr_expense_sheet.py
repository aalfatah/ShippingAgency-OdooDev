# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class HrExpenseSheet(models.Model):
    _name = "hr.expense.sheet"
    _inherit = ["hr.expense.sheet", "tier.validation"]
    _state_from = ["submit"]
    _state_to = ["approve", "post", "done"]

    _tier_validation_manual_config = False

    def validate_tier(self):
        super(HrExpenseSheet, self).validate_tier()
        if not self.review_ids.filtered(lambda r: r.status != 'approved'):
            return self.approve_expense_sheets()

    def _get_tier_validation_readonly_domain(self):
        return [] # [("review_ids", "!=", [])]

    def get_approval_level(self):
        return len(self.review_ids)

    def get_approval(self, level, option):
        user_id = False
        if level == 1 and len(self.review_ids) >= 1:
            user_id = self.review_ids[0].done_by
            todo_by = self.review_ids[0].todo_by
        elif level == 2 and len(self.review_ids) >= 2:
            user_id = self.review_ids[1].done_by
            todo_by = self.review_ids[1].todo_by
        elif level == 3 and len(self.review_ids) >= 3:
            user_id = self.review_ids[2].done_by
            todo_by = self.review_ids[2].todo_by
        if user_id:
            employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', user_id.id)])
            if option == 'name':
                return employee_id.name
            elif option == 'job_title':
                return employee_id.job_title
            elif option == 'signature':
                return user_id.signature
        else:
            if option == 'name':
                return todo_by
        return False
