from odoo import fields, models, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    contract_expiry_status = fields.Selection([('H4', '> 60 Days'),
                                               ('H3', '60 <= Days < 30'),
                                               ('H2', '30 <= Days < 14'),
                                               ('H1', '<= 14 Days '),
                                               ('H0', 'Expired'),
                                               ('H', 'No Contract')],
                                              string='Contract Status', compute='_get_contract_expiry_status',
                                              groups='hr_contract.group_hr_contract_employee_manager', store=True)

    @api.depends('contract_id', 'contract_id.contract_type_id',
                 'contract_id.state', 'contract_id.kanban_state', 'contract_id.days_exp')
    def _get_contract_expiry_status(self):
        for emp in self:
            last_contract_id = self.env['hr.contract'].search([('employee_id', '=', emp.id), ('state' ,'in' ,('open' ,'close'))], order='date_start desc', limit=1)
            if last_contract_id:
                if last_contract_id.days_exp > 60:
                    emp.contract_expiry_status = 'H4'
                elif last_contract_id.days_exp > 30:
                    emp.contract_expiry_status = 'H3'
                elif last_contract_id.days_exp > 14:
                    emp.contract_expiry_status = 'H2'
                elif last_contract_id.days_exp >= 0:
                    emp.contract_expiry_status = 'H1'
                else:
                    emp.contract_expiry_status = 'H0'
            else:
                emp.contract_expiry_status = 'H'
