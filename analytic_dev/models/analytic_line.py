from odoo import models, fields

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    # Mengambil data dari account.move melalu move_line_id
    activity_period_from = fields.Date(
        related='move_line_id.activity_period_from', 
        string='Date From', 
        store=True, 
        readonly=True
    )
    activity_period_to = fields.Date(
        related='move_line_id.activity_period_to', 
        string='Date To', 
        store=True, 
        readonly=True
    )