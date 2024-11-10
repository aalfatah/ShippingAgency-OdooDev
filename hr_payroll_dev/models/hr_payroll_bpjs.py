from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp


class HrPayrollBpjs(models.Model):
    _name = "hr.payroll.bpjs"
    _description = 'HR Payroll bpjs'

    name = fields.Char(string='BPJS')
    code = fields.Char(string='Code')
    bpjs_type = fields.Selection([('kesehatan', 'BPJS Kesehatan'), ('tenaga_kerja', 'BPJS Tenaga Kerja')], string="BPJS Type")
    rate_company = fields.Float(string="Rate Company (%)")
    rate_employee = fields.Float(string="Rate Employee (%)")
    max_upah = fields.Float(string="Upah Maximum")
    min_upah = fields.Float(string="Upah Minimum")
    unit_kerja = fields.Selection([('administrasi','Administrasi'), ('pabrikasi','Pabrikasi'), ('tambang','Tambang')],  string="Unit Kerja")

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'The BPJS must be unique!')
    ]
