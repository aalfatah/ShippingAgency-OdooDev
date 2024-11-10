# coding: utf-8
from odoo import api, fields, models
from datetime import datetime, timedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    other_input_ids = fields.One2many('hr.payroll.other.input.line', 'employee_id', string='Other Payroll Input', readonly=False)


class HrPayrollOtherInputLine(models.Model):
    _name = 'hr.payroll.other.input.line'
    _description = "hr.payroll.other.input.line"

    name = fields.Many2one('hr.rule.input', string='Other Input', required=True)
    date_from = fields.Date('Date from', default=lambda self: datetime.today(), required=True)
    date_to = fields.Date('Date to')
    amount = fields.Float('Amount', required=True)
    employee_id = fields.Many2one('hr.employee', "Employee", ondelete='cascade')


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    @api.model
    def get_inputs(self, contracts, date_from, date_to):
        res = []

        structure_ids = contracts.get_all_structures()
        rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]
        inputs = self.env['hr.salary.rule'].browse(sorted_rule_ids).mapped('input_ids')

        for contract in contracts:
            employee_id = (self.employee_id and self.employee_id.id) or (contract.employee_id and contract.employee_id.id)
            for input in inputs:
                amount = 0.0
                other_input_line = self.env['hr.payroll.other.input.line'].search([('employee_id', '=', employee_id),('name', '=', input.id),
                                                                            '|','&',('date_from', '>=', date_from),('date_to', '<=', date_to),
                                                                            '&',('date_from', '<=', date_from),('date_to', '=', False),
                                                                            ])
                for line in other_input_line:
                    amount += line.amount
                input_data = {
                    'name': input.name,
                    'code': input.code,
                    'amount': amount,
                    'contract_id': contract.id,
                }
                res += [input_data]
        return res
