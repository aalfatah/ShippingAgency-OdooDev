from odoo import _, api, fields, models


class ApprovalTitle(models.Model):
	_name = "approval.title"
	_description = "Approval Title"
	_order = 'sequence, id'

	name = fields.Char(string='Approval Title', required=True, help="Name")
	level = fields.Integer(string='Approval Level', required=True, help="Level")
	sequence = fields.Integer(help="Gives the sequence when displaying a list of approval.", default=10)
