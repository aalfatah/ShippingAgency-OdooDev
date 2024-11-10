from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp


class HrPayrollPkp(models.Model):
    _name = "hr.payroll.pkp"
    _description = 'HR Payroll PKP'

    name = fields.Char(string='PKP', required=True)
    max_income = fields.Float(string="Max Income", digits=2) #dp.get_precision('Payroll'))
    tax_rate_npwp = fields.Float(string="Rate with NPWP")
    tax_rate_no_npwp = fields.Float(string="Rate w/o NPWP")
    # validity_start = fields.Date(string="Validity Start")
    # validity_end = fields.Date(string="Validity End")
    # active = fields.Boolean(string="Active", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The PKP must be unique!')
    ]

    # def archived(self):
    #     self.active = False
    #
    # def unarchived(self):
    #     self.active = True
