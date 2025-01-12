from odoo import _, api, fields, models


class ExpenseSheetApproval(models.Model):
	_name = "hr.expense.sheet.approval"
	_description = "Expense Approval"

	name = fields.Selection([
		# ('expense_request', 'Expense Request'),
		('expense_approver1', 'Expense Approver 1'),
		('expense_approver2', 'Expense Approver 2'),
	], required=True)
	limit = fields.Float("Limit Amount", required=True)
	approver = fields.Many2one("res.groups", "Approver")
