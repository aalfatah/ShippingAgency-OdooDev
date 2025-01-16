from odoo import fields, models, api
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.model
    def _bypass_fields_to_synchronize(self):
        return (
            'payment_transfer_approver1_id', 'payment_transfer_approver2_id'
        )

    def _synchronize_to_moves(self, changed_fields):
        # EXTENDS account
        if any(field_name in changed_fields for field_name in self._bypass_fields_to_synchronize()):
            return
        return super()._synchronize_to_moves(changed_fields)
