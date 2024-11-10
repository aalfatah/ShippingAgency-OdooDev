# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    travel_expense = fields.Boolean('is a travel expense', default=False)

    @api.constrains('expense_line_ids', 'employee_id')
    def _check_employee(self):
        for sheet in self:
            if sheet.travel_expense == True:
                pass
            else:
                return super(ExpenseSheet, self)._check_employee()
