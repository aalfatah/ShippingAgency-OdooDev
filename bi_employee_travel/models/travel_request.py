# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import datetime
from odoo.exceptions import Warning, UserError
from odoo.exceptions import UserError, ValidationError


class TravelRequest(models.Model):
    _name = "travel.request"
    _description = "Travel Request"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    department_manager_id = fields.Many2one('hr.employee', string="Manager")
    department_id = fields.Many2one('hr.department', string="Department")
    job_id = fields.Many2one('hr.job', string="Job Position")
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id.id, readonly=True)

    request_by = fields.Many2one('hr.employee', string="Requested By")
    confirm_by = fields.Many2one('res.users', string="Confirmed By")
    approve_by = fields.Many2one('res.users', string="Approved By")

    req_date = fields.Date(string="Request Date")
    confirm_date = fields.Date(string="Confirm Date")
    approve_date = fields.Date(string="Approved Date")

    expense_sheet_id = fields.Many2one('hr.expense.sheet', string="Created Expense Sheet", readonly=True)

    travel_purpose = fields.Char(string="Travel Purpose", required=True)
    project_id = fields.Many2one('project.task', string="Project", required=False)
    account_analytic_id = fields.Many2one('account.analytic.account', string="Analytic Account")

    from_city = fields.Char('From City')
    from_state_id = fields.Many2one('res.country.state', string="From State")
    from_country_id = fields.Many2one('res.country', string="From Country")

    to_street = fields.Char('Street')
    to_street_2 = fields.Char('Street2')
    to_city = fields.Char('To City')
    to_state_id = fields.Many2one('res.country.state', string="To State")
    to_country_id = fields.Many2one('res.country', string="To Country")
    to_zip_code = fields.Char('Zip')

    req_departure_date = fields.Datetime(string="Request Departure Date", required=True)
    req_return_date = fields.Datetime(string="Request Return Date", required=True)
    days = fields.Char('Days', compute="_compute_days")
    req_travel_mode_id = fields.Many2one('travel.mode', string="Request Mode Of Travel")
    return_mode_id = fields.Many2one('travel.mode', string="Return Mode")

    phone_no = fields.Char('Contact Number')
    email = fields.Char('Email')

    available_departure_date = fields.Datetime(string="Available Departure Date")
    available_return_date = fields.Datetime(string="Available Return Date")
    departure_mode_travel_id = fields.Many2one('travel.mode', string="Departure Mode Of Travel")
    return_mode_travel_id = fields.Many2one('travel.mode', string="Return Mode Of Travel")
    visa_agent_id = fields.Many2one('res.partner', string="Visa Agent")
    ticket_booking_agent_id = fields.Many2one('res.partner', string="Ticket Booking Agent")

    bank_id = fields.Many2one('res.bank', string="Bank Name")
    cheque_number = fields.Char(string="Cheque Number")

    advance_ids = fields.One2many('hr.expense', 'travel_id', string="Cash Advance")
    expense_ids = fields.One2many('hr.expense', 'travel_expense_id', string="Expenses")

    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('approved', 'Approved'), ('rejected', 'Rejected'),
         ('returned', 'Returned'), ('submitted', 'Expenses Submitted')], default="draft", string="States",
        tracking=True)

    @api.onchange('employee_id')
    def onchange_employee(self):
        self.department_manager_id = self.employee_id.parent_id.id
        self.job_id = self.employee_id.job_id.id
        self.department_id = self.employee_id.department_id.id
        return

    @api.constrains('req_departure_date', 'req_return_date', 'available_departure_date', 'available_return_date')
    def check_dates(self):
        if self.req_departure_date > self.req_return_date:
            raise Warning(_('Request Return Date should be after the Request Departure Date!!'))

        if self.available_departure_date > self.available_return_date:
            raise Warning(_('Available Departure Date should be after the Available Return Date!!'))

    @api.model
    def create(self, vals):
        # seq = self.env['ir.sequence'].next_by_code('travel.request') or '/'
        # vals['name'] = seq
        vals['request_by'] = vals['employee_id']
        vals['req_date'] = fields.datetime.now()
        if 'project_id' in vals:
            project_obj = self.env['project.task'].browse(vals['project_id'])
            reg = self.env['account.analytic.account'].search([('name', '=', project_obj.name)], limit=1)
            if reg:
                vals['account_analytic_id'] = reg.id
            else:
                if project_obj.name:
                    value = project_obj.name
                    analytic = self.env['account.analytic.account'].create({
                        'name': project_obj.name,
                    })
                    vals['account_analytic_id'] = analytic.id
        res = super(TravelRequest, self).create(vals)
        return res

    def write(self, vals):
        if 'project_id' in vals:
            project_obj = self.env['project.task'].browse(vals['project_id'])
            reg = self.env['account.analytic.account'].search([('name', '=', project_obj.name)], limit=1)
            if reg:
                vals['account_analytic_id'] = reg.id
            else:
                if project_obj.name:
                    value = project_obj.name
                    analytic = self.env['account.analytic.account'].create({
                        'name': project_obj.name,
                    })
                    vals['account_analytic_id'] = analytic.id

        return super(TravelRequest, self).write(vals)

    def action_expense_sheet(self):
        return {
            'name': 'Expense',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'context': {},
            'res_model': 'hr.expense',
            'domain': [('id', 'in', self.expense_ids.ids)],
        }

    def action_confirm(self):
        self.write({'state': 'confirmed', 'confirm_date': fields.datetime.now(),
                    'confirm_by': self.env.user.id})
        return

    def action_approve(self):
        self.write({'state': 'approved', 'approve_date': fields.datetime.now(),
                    'approve_by': self.env.user.id})
        return

    def return_from_trip(self):
        self.write({'state': 'returned'})
        id_lst = []
        for line in self.advance_ids:
            id_lst.append(line.id)
        self.expense_ids = [(6, 0, id_lst)]
        return

    def action_create_expense(self):
        id_lst = []
        for line in self.expense_ids:
            id_lst.append(line.id)
        res = self.env['hr.expense.sheet'].create(
            {'name': self.travel_purpose, 'employee_id': self.employee_id.id, 'travel_expense': True,
             'expense_line_ids': [(6, 0, id_lst)]})

        self.expense_sheet_id = res.id
        self.write({'state': 'submitted'})

        return

    def action_draft(self):
        self.write({'state': 'draft'})
        return

    def action_reject(self):
        self.write({'state': 'rejected'})
        return

    @api.depends('req_departure_date', 'req_return_date')
    def _compute_days(self):

        for line in self:
            line.days = False
            if line.req_departure_date and line.req_return_date:
                diff = line.req_return_date - line.req_departure_date
                mini = diff.seconds // 60
                hour = mini // 60
                sec = (diff.seconds) - (mini * 60)
                miniute = mini - (hour * 60)
                time = str(diff.days) + ' Days, ' + ("%d:%02d.%02d" % (hour, miniute, sec))
                line.days = time
        return
