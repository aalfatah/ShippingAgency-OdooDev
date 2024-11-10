# -*- encoding: utf-8 -*-
import csv
import base64
import time

from xlrd import open_workbook
from datetime import datetime
from calendar import monthrange

from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_is_zero, float_compare


class PayrollOtherInputEmployee(models.TransientModel):
    _name = 'payroll.other.input.employee'
    _description = "payroll.other.input.employee"

    @api.model
    def _get_default_date_from(self):
        date = fields.Date.from_string(fields.Date.today())
        date_from = '%s-%s-01' % (date.year, str(date.month).zfill(2))
        return date_from

    @api.model
    def _get_default_date_to(self):
        date = fields.Date.from_string(fields.Date.today())
        end_of_month = monthrange(date.year, date.month)[1]
        date_to = '%s-%s-%s' % (date.year, str(date.month).zfill(2), end_of_month)
        return date_to

    # Fields
    type = fields.Selection([('employee', 'By employee'), ('all', 'All employee')], 'Type', readonly=False,
                            required=True, default='employee')
    date_from = fields.Date(string='Date from', default=_get_default_date_from, required=True,
                            help='Date from which the assignment for payroll calculation will be taken into account')
    date_to = fields.Date(string='Date to', default=_get_default_date_to,
                          help='Date until which the allocation for payroll calculation will be taken into account')
    rule_input_id = fields.Many2one('hr.rule.input', string='Other Input', required=True)
    load_employees = fields.Boolean('Load All',
                                    help="If the assignment will be made to all active employees, select this option to load them all.")
    other_input_employee_ids = fields.One2many('payroll.other.input.employee.line', 'other_input_employee_id',
                                               'Other Input by employee')
    amount = fields.Float('Amount', required=False, help="Admission amount for payroll calculation.")
    employee_ids = fields.Many2many('hr.employee', 'other_input_payroll_employee_rel', 'other_input_id', 'employee_id',
                                    'Employee')
    employee_data_ids = fields.Many2many('hr.employee', 'other_input_payroll_employee_data_rel', 'other_input_id',
                                         'employee_id', 'Employee Data')
    file_ids = fields.Many2many(string='Employee File', comodel_name='ir.attachment')
    file_name = fields.Char('File name', related='file_ids.name')

    @api.onchange('load_employees')
    def onchange_load_employees(self):
        if self.load_employees:
            employees = self.env['hr.employee'].search([('active', '=', True)])
            self.other_input_employee_ids = [(0, 0, {'employee_id': employee.id}) for employee in employees]
        else:
            self.other_input_employee_ids = False

    def assign_other_input(self):
        other_input_line_obj = self.env['hr.payroll.other.input.line']
        account_precision = self.env['decimal.precision'].precision_get('Account')
        if self.type == 'employee':
            for line in self.other_input_employee_ids:
                if not float_is_zero(line.amount, account_precision):
                    other_input = other_input_line_obj.search([
                        ('name', '=', self.rule_input_id.id),
                        ('employee_id', '=', line.employee_id.id),
                        ('date_from', '=', self.date_from),
                        ('date_to', '=', self.date_to),
                    ])
                    if other_input:
                        other_input.write({
                            'amount': line.amount,
                            'date_from': self.date_from,
                            'date_to': self.date_to,
                        })
                    else:
                        other_input_line_obj.create({
                            'name': self.rule_input_id.id,
                            'employee_id': line.employee_id.id,
                            'amount': line.amount,
                            'date_from': self.date_from,
                            'date_to': self.date_to,
                        })
        else:
            if not float_is_zero(self.amount, account_precision):
                for employee in self.employee_ids:
                    other_input = other_input_line_obj.search([
                        ('name', '=', self.rule_input_id.id),
                        ('employee_id', '=', employee.id),
                    ])
                    if other_input:
                        other_input.write({
                            'amount': self.amount,
                            'date_from': self.date_from,
                            'date_to': self.date_to,
                        })
                    else:
                        other_input_line_obj.create({
                            'name': self.rule_input_id.id,
                            'employee_id': employee.id,
                            'amount': self.amount,
                            'date_from': self.date_from,
                            'date_to': self.date_to,
                        })

    @api.onchange('file_ids')
    def onchange_file_ids(self):
        if self.file_ids:
            self.read_document()

    def read_document(self):
        file = self.file_ids
        payment_receipt_lines = []
        if file.datas:
            data_file = base64.b64decode(file.datas)
            wb = open_workbook(file_contents=data_file)
            sheet = wb.sheet_by_index(0)
            for row in range(1, sheet.nrows):
                if not (sheet.cell_value(row, 1) == '' and sheet.cell_value(row, 1) == ''):
                    identification = self.check_field_identification(sheet.cell(row, 0), row)
                    amount = self.check_field_amount(sheet.cell_value(row, 2), row)
                    payment_receipt_lines.append((0, 0, {'employee_id': identification, 'amount': amount}))
        self.other_input_employee_ids = payment_receipt_lines

    def check_field_amount(self, field, nrows):
        if not field:
            raise UserError(
                'The amount field is empty in row %s, complete all the fields in the file.' % str(nrows + 1))
        if field < 0:
            raise UserError(
                'The amount %0.2f is negative in row %s, you cannot assign a negative entry.' % (field, str(nrows + 1)))
        else:
            return float(field)

    def check_field_identification(self, field, nrows):
        employee = self.env['hr.employee']
        if not field:
            raise UserError(
                'The identification field is empty in row %s, complete all the fields in the file.' % str(nrows + 1))
        else:
            employee_ids = employee.search([('nrp', '=', field.value), ('active', '=', True)])
            if not employee_ids:
                raise UserError('No results found for NRP %s, in row %s.' % (str(field), str(nrows + 1)))
            elif len(employee_ids) > 1:
                raise UserError(
                    'Duplicate NRP %s employee: %s' % (field.value, ', '.join(e.name for e in employee_ids)))
            else:
                return employee_ids.id

    def download_employee_data(self):
        return self.env.ref('hr_payroll_other_inputs.action_report_data_employees_excel').report_action(self)


class PayrollOtherInputEmployeeLine(models.TransientModel):
    _name = 'payroll.other.input.employee.line'
    _description = "payroll.other.input.employee.line"

    other_input_employee_id = fields.Many2one('payroll.other.input.employee')
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    amount = fields.Float('Amount', required=True, help="Admission amount for payroll calculation.")
