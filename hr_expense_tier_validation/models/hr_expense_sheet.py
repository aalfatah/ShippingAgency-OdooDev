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
            self.approve_expense_sheets()
