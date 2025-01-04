from odoo import fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _get_report_base_filename(self):
        self.ensure_one()
        if self.is_internal_transfer:
            return 'Internal Transfer %s' % self.name
        elif self.payment_type == 'outbound':
            return 'Payment Voucher %s - %' % (self.name, self.partner_id.name)
        elif self.payment_type == 'inbound':
            return 'Receive Voucher %s - %' % (self.name, self.partner_id.name)
