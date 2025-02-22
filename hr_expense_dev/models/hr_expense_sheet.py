from odoo import fields, models, api, _
from datetime import date, timedelta, datetime
from odoo.tools import email_split, float_is_zero
from odoo.exceptions import UserError, ValidationError


class ExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    def _prepare_bill_vals(self):
        self.ensure_one()
        res = super(ExpenseSheet, self)._prepare_bill_vals()
        # res["move_type"] = "entry"
        return res

    def _do_create_moves(self):
        moves = super(ExpenseSheet, self)._do_create_moves()
        # moves.move_type = 'entry'
        # moves.move_type = 'in_invoice' # odoo 16, expense di perlakukan seperti vendor bill
        return moves
