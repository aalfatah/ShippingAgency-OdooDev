from odoo import fields, models, api
from datetime import date
from dateutil.relativedelta import relativedelta


class Employee(models.Model):
    _inherit = 'hr.employee'

    ptkp_id = fields.Many2one('hr.payroll.ptkp', string='PTKP', groups='hr.group_hr_user')
    bpjstk_status = fields.Boolean(string='BPJS Ketenagakerjaan Status', groups='hr.group_hr_user')
    bpjstk_no = fields.Char(string='BPJS Ketenagakerjaan', related="address_home_id.bpjstk_no", store=True, groups='hr.group_hr_user')
    bpjsks_status = fields.Boolean(string="BPJS Kesehatan Status", groups='hr.group_hr_user')
    bpjsks_no = fields.Char(string='BPJS Kesehatan', related="address_home_id.bpjsks_no", store=True, groups='hr.group_hr_user')
    unit_kerja = fields.Selection([('administrasi','Administrasi'), ('pabrikasi','Pabrikasi'), ('tambang','Tambang')],  string="Unit Kerja", groups='hr.group_hr_user')
    payslip_password = fields.Char(string="Payslip Password", help="Set Password on pdf document.", compute="_get_payslip_password")
    payslip_email = fields.Boolean(string="Send Payslip Email", groups='hr.group_hr_user')

    def _get_payslip_password(self):
        for row in self:
            payslip_password = False
            if row.birthday:
                d = int(row.birthday.day)
                if d < 10:
                    d = '0'+str(d)
                d = str(d)

                m = int(row.birthday.month)
                if m < 10:
                    m = '0'+str(m)
                m = str(m)

                y = str(row.birthday.year)
                payslip_password = d+m+y
            row.payslip_password = payslip_password

    def update_contact(self, vals):
        if self.address_home_id:
            contact = {}
            if 'bpjstk_no' in vals:
                contact['bpjstk_no'] = vals.get('bpjstk_no')
            if 'bpjsks_no' in vals:
                contact['bpjsks_no'] = vals.get('bpjsks_no')
            if contact:
                self.address_home_id.update(contact)

    @api.model_create_multi
    def create(self, vals):
        ret = super(Employee, self).create(vals)
        self.update_contact(vals)
        return ret

    def write(self, vals):
        self.update_contact(vals)
        return super(Employee, self).write(vals)
