from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp


class HrPayrollPtkp(models.Model):
    _name = "hr.payroll.ptkp"
    _description = 'PTKP'

    name = fields.Char(string='PTKP', required=True)
    tarif = fields.Float(string="Tarif", digits=2) #dp.get_precision('Payroll'))

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'The PTKP code must be unique!')
    ]
