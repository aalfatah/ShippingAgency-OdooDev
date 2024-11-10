from odoo import fields, models, api, _
from odoo.exceptions import UserError


class HrContractPayrollUpdate(models.Model):
    _inherit = 'hr.contract.payroll.update'

    salary_rule = fields.Selection(selection='_get_salary_rules') #, states=READONLY_STATES, required=True, string="Salary Rule")

    @api.model
    def _get_salary_rules(self):
        return [('tramp', 'Tunjangan Tramp')]