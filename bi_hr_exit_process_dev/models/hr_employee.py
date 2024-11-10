from odoo import models, fields, api, _
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    exit_request_id = fields.Many2one('exit.request', 'Resign Id', compute='_get_termination')
    resign_date = fields.Date('Resign Date', readonly=True, help="Date of the resignation", groups='hr.group_hr_user')
    lama_kerja = fields.Char(string='Lama Kerja' , compute= '_lama_kerja') #, store=True)

    def _get_termination(self):
        for emp in self:
            emp.exit_request_id = self.env['exit.request'].sudo().search([('employee_id', '=', emp.id)], limit=1).id

    @api.depends('active','first_contract_date','resign_date','contract_id','contract_id.first_contract_date')
    def _lama_kerja(self):
        for row in self:
            lama = ''
            # if row.contract_id.first_contract_date:
            if row.first_contract_date:
                # join_date = row.contract_id.first_contract_date
                join_date = row.first_contract_date
                if row.active:
                    end_date = date.today()
                else:
                    end_date = row.resign_date
                rdelta = relativedelta(end_date, join_date)
                years = str(rdelta.years)
                months = str(rdelta.months)
                days = str(rdelta.days)
                lama = years +' Tahun ' + months +' Bulan ' + days +' Hari'

            row.lama_kerja = lama
