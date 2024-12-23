# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import Warning
import datetime
from datetime import datetime, timedelta
from odoo.exceptions import UserError

FORMATROMAN = (
    ('M',  1000),
    ('CM', 900),
    ('D',  500),
    ('CD', 400),
    ('C',  100),
    ('XC', 90),
    ('L',  50),
    ('XL', 40),
    ('X',  10),
    ('IX', 9),
    ('V',  5),
    ('IV', 4),
    ('I',  1)
)


class EmployeeTransferDev(models.Model):
    _inherit = 'employee.transfer'
    _description = 'Employee Transfer'
    _order = "date desc"

    transfer_type = fields.Selection([('area', 'AREA'), ('level', 'LEVEL'), ('organization', 'ORGANIZATION')], string='Transfer Type' )
    document_type = fields.Many2one('employee.transfer.document', string='Document Type')

    department_id_prev = fields.Many2one('hr.department', string='Department', readonly="1")
    department_id = fields.Many2one('hr.department', string='Department')
    job_id_prev = fields.Many2one('hr.job', 'Job Position', readonly="1")
    job_id = fields.Many2one('hr.job', 'Job Position')
    area_id_prev = fields.Many2one('res.area', string='Area', readonly="1")
    area_id = fields.Many2one('res.area', string='Area')
    parent_id_prev = fields.Many2one('hr.employee', string='Manager', readonly="1")
    parent_id = fields.Many2one('hr.employee', string='Manager')
    # tax_status_prev = fields.Many2one('hr.payroll.ptkp', string='Tax Status', readonly="1")
    # tax_status = fields.Many2one('hr.payroll.ptkp', string='Tax Status')

    # line_ids = fields.One2many('employee.transfer.line','transfer_id')
    state = fields.Selection(selection='_get_state', string='Status', readonly=True, copy=False, default='draft')
    remarks = fields.Char(string="Remarks", readonly=True)

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            employee = self.env['hr.employee'].browse(self.employee_id.id)
            self.department_id_prev = employee.department_id.id
            self.job_id_prev = employee.job_id.id
            self.area_id_prev = employee.area_id.id
            self.parent_id_prev = employee.parent_id.id
            self.department_id = employee.department_id.id
            self.job_id = employee.job_id.id
            self.area_id = employee.area_id.id
            self.parent_id = employee.parent_id.id

    @api.model
    def _get_state(self):
        return [('draft', 'New'), ('cancel', 'Cancelled'), ('done', 'Done')]

    def transfer(self):
        val = {}
        remark_string = ''
        if self.department_id_prev != self.department_id:
            val.update({'department_id': self.department_id.id})
            remark_string += 'Department : ' + str(self.department_id_prev.name) + ' to ' + str(self.department_id.name)
        
        if self.job_id_prev != self.job_id:
            val.update({'job_id': self.job_id.id})
            remark_string += ', ' if remark_string else ''
            remark_string += 'Job Position : ' + str(self.job_id_prev.name) + ' to ' + str(self.job_id.name)

        if self.area_id_prev != self.area_id:
            val.update({'area_id': self.area_id.id})
            remark_string += ', ' if remark_string else ''
            remark_string += 'Area : ' + str(self.area_id_prev.name) + ' to ' + str(self.area_id.name)

        if self.parent_id_prev != self.parent_id:
            val.update({'parent_id': self.parent_id.id})
            remark_string += ', ' if remark_string else ''
            remark_string += 'Manager : ' + str(self.parent_id_prev.name) + ' to ' + str(self.parent_id.name)

        self.remarks = remark_string

        obj_employee = self.env['hr.employee'].sudo().search([('id', '=', self.employee_id.id)])
        obj_employee.write(val)

        self.state = 'done'

    def cancel_transfer(self):
        remark_string = 'Cancel'
        obj_emp = self.env['hr.employee'].browse(self.employee_id.id)
        emp = {
                    'department_id': self.department_id_prev.id,
                    'job_id': self.job_id_prev.id,
                    'area_id': self.area_id_prev.id,
                    'parent_id': self.parent_id_prev.id,
                }
        self.remarks = remark_string
        obj_emp.write(emp)
        self.state = 'cancel'

    def set_to_draft(self):
        self.state = 'draft'

    def convert_to_roman(self, n):
        result = ""
        for numeral, integer in FORMATROMAN:
            while n >= integer:
                result += numeral
                n -= integer
        return result

    @api.model
    def create(self, vals):
        date = vals['date']
        tanggal = datetime.strptime(date, '%Y-%m-%d')
        year = tanggal.strftime("%Y")
        month = tanggal.strftime("%m")
        rom_month = self.convert_to_roman(int(month))
        doc_type = self.env['employee.transfer.document'].search([('id', '=', vals['document_type'])], limit=1).name

        if vals.get('name', _('New')) == _('New'):
            seq  = self.env['ir.sequence'].next_by_code('employee.transfer.seq')
            if vals['document_type'] and vals['date']:
                sequence = seq.replace('transfer', doc_type+'/' + rom_month + '/' + year)
            else :
                sequence = seq.replace('/transfer', '')

            vals['name'] = sequence

        res = super(EmployeeTransferDev, self).create(vals)
        return res

    def write(self, vals):
        if vals.get('date'):
            date = vals.get('date')
            tanggal = datetime.strptime(date, '%Y-%m-%d')
        else:
            date = self.date
            tanggal = date

        year = tanggal.strftime("%Y")
        month = tanggal.strftime("%m")
        rom_month = self.convert_to_roman(int(month))
        seq = str(self.name)
        seq = seq[:9]
        
        if vals.get('document_type'):
            doc_type = self.env['employee.transfer.document'].search([('id', '=', vals.get('document_type'))],
                                                                     limit=1).name
        else:
            doc_type = self.document_type.name

        if doc_type and date:
            sequence = seq + doc_type + '/' + rom_month + '/' + year
        else:
            sequence = seq

        vals['name'] = sequence

        res = super(EmployeeTransferDev, self).write(vals)
        return res

    @api.onchange('transfer_type')
    def _type(self):
        types = self.env['employee.transfer.document'].search([('transfer_type', '=', self.transfer_type)], limit=1)
        self.document_type = types
        return {
            'domain': {'document_type': [('transfer_type', '=', self.transfer_type)]},
        }

    def unlink(self):
        for transfer in self:
            if transfer.state not in ('draft', 'cancel'):
                raise UserError(_('You can not delete a document. You must first cancel it.'))
        return super(EmployeeTransferDev, self).unlink()


class EmployeeTransferDocumentDev(models.Model):
    _name = 'employee.transfer.document'
    _description = 'Employee Transfer Document'

    transfer_type = fields.Char('Transfer Type')
    name = fields.Char(string='Document Type')
