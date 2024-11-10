from odoo import api, fields, models, _


class PayrollTER(models.Model):
    _name = "hr.payroll.ter"
    _description = 'TER Line'

    name = fields.Selection([('A', 'A'), ('B', 'B'), ('C', 'C')], string='TER', required=True)
    limit_gross = fields.Float('Limit Gross')
    rate = fields.Float('Rate')
