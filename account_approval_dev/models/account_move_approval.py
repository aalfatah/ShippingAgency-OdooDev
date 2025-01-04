from odoo import _, api, fields, models


class AccountMoveApproval(models.Model):
	_name = "account.move.approval"
	_description = "Account Move Approval"

	name = fields.Selection([#('invoice_approver', 'Invoice Approver'),
							 ('bill_approver1', 'Bill Reviewer'),
							 ('bill_approver2', 'Bill Approver'),
							 # ('transfer_prepared', 'Transfer Prepared By'),
							 # ('transfer_approver1', 'Transfer Approver 1'),
							 # ('transfer_approver2', 'Transfer Approver 2'),
							 # ('move_approver1', 'Journal Approver 1'),
							 # ('move_approver2', 'Journal Approver 2'),
							 ], required=True)
	limit = fields.Float("Limit Amount", required=True)
	approver = fields.Many2one("res.groups", "Approver")
	journal_ids = fields.Many2many(comodel_name="account.journal",
								   relation="move_approval_journal_rel",
								   column1="approval_id",
								   column2="journal_id",
								   string="Journals"
	)