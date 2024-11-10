from odoo import api, fields, models, _


class HrPayrollPtkp(models.Model):
    _inherit = "hr.payroll.ptkp"

    ter = fields.Selection([('A', 'A'), ('B', 'B'), ('C', 'C')], string='TER', required=True)
