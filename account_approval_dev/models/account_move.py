# Copyright 2017 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    # customer invoice
    # signed_invoice_approval1_id = fields.Many2one(comodel_name="res.users", string="Invoice Approver 1")
    # invoice_approval1_domain = fields.Char(compute='_get_signed_domain', readonly=True, store=False)

    # vendor bill
    bill_signed1_id = fields.Many2one(comodel_name="res.users", string="Verifier")
    bill_signed2_id = fields.Many2one(comodel_name="res.users", string="Approver")
    bill_approval1_ids = fields.Many2many('res.users', 'res_users_bill_approval1_bill', compute='_get_signed_domain')
    bill_approval2_ids = fields.Many2many('res.users', 'res_users_bill_approval2_bill', compute='_get_signed_domain')

    # journal entry
    # move_signed1_id = fields.Many2one(comodel_name="res.users", string="Journal Approver 1") #, domain=lambda self: self._get_bill_signed1_domain())
    # move_signed2_id = fields.Many2one(comodel_name="res.users", string="Journal Approver 2") #, domain=lambda self: self._get_bill_signed2_domain())
    # move_approval1_domain = fields.Char(compute='_get_signed_domain', readonly=True, store=False)
    # move_approval2_domain = fields.Char(compute='_get_signed_domain', readonly=True, store=False)

    # approver1_id = fields.Many2one('approval.title', 'Reviewer', domain=[('level', '=', 1)])
    # approver2_id = fields.Many2one('approval.title', 'Approver', domain=[('level', '=', 2)])

    def _get_approval(self, approval_type, limit_amount):
        return self.env['account.move.approval'].search([('name', '=', approval_type), ('limit', '<=', limit_amount)],
                                                        order="limit desc", limit=1)

    @api.depends('amount_total')
    def _get_signed_domain(self):
        for rec in self:
            # # if rec.move_type == 'out_invoice':
            # # approval = self.env['account.move.approval'].search([('name', '=', 'invoice_approver'), ('limit', '<=', rec.amount_total)], order="limit desc", limit=1)
            # rec.invoice_approval1_domain = json.dumps([('id', 'in', rec._get_approval('invoice_approver', rec.amount_total).approver.users.ids)])
            # # elif rec.move_type == 'in_invoice':
            # # approval = self.env['account.move.approval'].search([('name', '=', 'bill_approver1'), ('limit', '<=', rec.amount_total)], order="limit desc", limit=1)

            rec.bill_approval1_ids = rec._get_approval('bill_approver1', rec.amount_total).approver.users.ids
            rec.bill_approval2_ids = rec._get_approval('bill_approver2', rec.amount_total).approver.users.ids

            # rec.move_approval1_domain = json.dumps([('id', 'in', rec._get_approval('move_approver1', rec.amount_total).approver.users.ids)])
            # rec.move_approval2_domain = json.dumps([('id', 'in', rec._get_approval('move_approver2', rec.amount_total).approver.users.ids)])

    def set_signed_id(self):
        self.ensure_one()
        # if self.move_type == 'out_invoice':
        #     approval = self.env['account.move.approval'].search([('name', '=', 'invoice_approver'),
        #                                                          ('limit', '<=', self.amount_total)],
        #                                                         order="limit desc", limit=1)
        #     self.signed_invoice_approval1_id = self.signed_invoice_approval1_id or (approval.approver.users[0].id
        #                                                                             if len(approval.approver.users)
        #                                                                             else False)
        # elif self.move_type == 'in_invoice':

        if self.move_type == 'in_invoice':
            approval = self.env['account.move.approval'].search([('name', '=', 'bill_approver1'),
                                                                 ('limit', '<=', self.amount_total)],
                                                                order="limit desc", limit=1)
            self.bill_signed1_id = approval.approver.users[0].id if len(approval.approver.users) else False
            approval = self.env['account.move.approval'].search([('name', '=', 'bill_approver2'),
                                                                 ('limit', '<=', self.amount_total)],
                                                                order="limit desc", limit=1)
            self.bill_signed2_id = approval.approver.users[0].id if len(approval.approver.users) else False

        # elif self.move_type == 'entry':
        #     approval = self.env['account.move.approval'].search([('name', '=', 'move_approver1'), ('journal_ids', '=', self.journal_id.id), ('limit', '<=', self.amount_total)], order="limit desc", limit=1)
        #     self.move_signed1_id = approval.approver.users[0].id if len(approval.approver.users) else False
        #     approval = self.env['account.move.approval'].search([('name', '=', 'move_approver2'), ('journal_ids', '=', self.journal_id.id), ('limit', '<=', self.amount_total)], order="limit desc", limit=1)
        #     self.move_signed2_id = approval.approver.users[0].id if len(approval.approver.users) else False

    @api.model
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        res.set_signed_id()
        return res

    # def get_employee(self, user_id):
    #     if user_id:
    #         return self.env['hr.employee'].sudo().search([('user_id', '=', user_id)])
    #     return False
