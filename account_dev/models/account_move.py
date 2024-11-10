from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    down_payment = fields.Boolean(string='Down Payment', tracking=True, default=False)
