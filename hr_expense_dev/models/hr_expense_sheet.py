from odoo import fields, models, api, _
# from datetime import date, timedelta, datetime
# from odoo.tools import email_split, float_is_zero
# from odoo.exceptions import UserError, ValidationError


class ExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    payment_mode = fields.Selection(store=True)
    bank_journal_id = fields.Many2one(tracking=True)

    @api.onchange('employee_id')
    def _set_employee_default_bank(self):
        if self.employee_id:
            self.bank_journal_id = self.employee_id.bank_journal_id.id

    def get_approval_level(self):
        return 2

    def get_approval(self, level, option):
        return False

    def get_requestor(self, option):
        employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', self.create_uid.id)])
        if option == 'name':
            return employee_id.name
        elif option == 'job_title':
            return employee_id.job_title
        elif option == 'signature':
            return self.create_uid.signature

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'bank_journal_id' not in vals and 'employee_id' in vals:
                employee_id = self.env['hr.employee'].sudo().browse(vals.get('employee_id'))
                vals.update({'bank_journal_id': employee_id.bank_journal_id.id})
        sheets = super(ExpenseSheet, self).create(vals_list)
        return sheets
