# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
# import json


class ExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    # request_signed_id = fields.Many2one(comodel_name="res.users", string="Request By")
    expense_signed1_id = fields.Many2one(comodel_name="res.users", string="Verifier") #, domain=lambda self: self._get_bill_signed1_domain())
    expense_signed2_id = fields.Many2one(comodel_name="res.users", string="Approver") #, domain=lambda self: self._get_bill_signed2_domain())
    # expense_request_domain = fields.Char(compute='_get_signed_domain', readonly=True, store=False)
    # expense_approval1_domain = fields.Char(compute='_get_signed_domain', readonly=True, store=False)
    # expense_approval2_domain = fields.Char(compute='_get_signed_domain', readonly=True, store=False)
    # expense_request_ids = fields.Many2many('res.users', 'res_users_expense_request', compute='_get_signed_domain')
    expense_approval1_ids = fields.Many2many('res.users', 'res_users_expense_approval1', compute='_get_signed_domain')
    expense_approval2_ids = fields.Many2many('res.users', 'res_users_expense_approval2', compute='_get_signed_domain')

    # expense_signed1_title = fields.Selection([('Manager FASC','Manager FASC'),('Direktur FASC','Direktur FASC')], string="Title Approver 1")
    # expense_signed2_title = fields.Selection([('Manager LS','Manager LS'),('Manager JS','Manager JS'),('Manager HCGAEHSCSR','Manager HCGAEHSCSR'),('Direktur Operation','Direktur Operation'),('Direktur HCGAEHSCSR','Direktur HCGAEHSCSR'),('Presiden Direktur','Presiden Direktur')], string="Title Approver 2")
    #
    # approver1_id = fields.Many2one('approval.title', 'Approver 1', domain=[('level', '=', 1)])
    # approver2_id = fields.Many2one('approval.title', 'Approver 2', domain=[('level', '=', 2)])

    def _get_approval(self, approval_type, limit_amount):
        return self.env['hr.expense.sheet.approval'].search([('name', '=', approval_type), ('limit', '<=', limit_amount)],
                                                            order="limit desc", limit=1)

    @api.depends('total_amount')
    def _get_signed_domain(self):
        for rec in self:
            # rec.expense_request_domain = json.dumps([('id', 'in', rec._get_approval('expense_request', rec.total_amount).approver.users.ids)])
            # rec.expense_approval1_domain = json.dumps([('id', 'in', rec._get_approval('expense_approver1', rec.total_amount).approver.users.ids)])
            # rec.expense_approval2_domain = json.dumps([('id', 'in', rec._get_approval('expense_approver2', rec.total_amount).approver.users.ids)])
            # rec.expense_request_ids = rec._get_approval('expense_request', rec.total_amount).approver.users.ids
            rec.expense_approval1_ids = rec._get_approval('expense_approver1', rec.total_amount).approver.users.ids
            rec.expense_approval2_ids = rec._get_approval('expense_approver2', rec.total_amount).approver.users.ids

    def _set_signed_id(self):
        self.ensure_one()
        approval = self.env['hr.expense.sheet.approval'].search([('name', '=', 'expense_approver1'), ('limit', '<=', self.total_amount)], order="limit desc", limit=1)
        self.expense_signed1_id = approval.approver.users[0].id if len(approval.approver.users) else False
        approval = self.env['hr.expense.sheet.approval'].search([('name', '=', 'expense_approver2'), ('limit', '<=', self.total_amount)], order="limit desc", limit=1)
        self.expense_signed2_id = approval.approver.users[0].id if len(approval.approver.users) else False

    def get_employee(self, user_id):
        return self.env['hr.employee'].sudo().search([('user_id', '=', user_id)])

    @api.model
    def create(self, vals):
        res = super(ExpenseSheet, self).create(vals)
        res._set_signed_id()
        return res
