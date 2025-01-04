# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json


class AccountPayment(models.Model):
    _inherit = "account.payment"

    # payment transfer
    payment_transfer_prepared_id = fields.Many2one(comodel_name="res.users", string="Prepared By")
    payment_transfer_approver1_id = fields.Many2one(comodel_name="res.users", string="Approver 1")
    payment_transfer_approver2_id = fields.Many2one(comodel_name="res.users", string="Approver 2")
    payment_transfer_prepared_domain = fields.Char(compute='_get_signed_domain', readonly=True, store=False)
    payment_transfer_approver1_domain = fields.Char(compute='_get_signed_domain', readonly=True, store=False)
    payment_transfer_approver2_domain = fields.Char(compute='_get_signed_domain', readonly=True, store=False)

    approver1_id = fields.Many2one('approval.title', 'Approver 1', domain=[('level', '=', 1)])
    approver2_id = fields.Many2one('approval.title', 'Approver 2', domain=[('level', '=', 2)])
    payment_transfer_received_by = fields.Char('Received By')

    def _get_approval(self, approval_type, limit_amount):
        return self.env['account.move.approval'].search([('name', '=', approval_type), ('limit', '<=', limit_amount)], order="limit desc", limit=1)

    @api.depends('amount_total')
    def _get_signed_domain(self):
        for rec in self:
            # payment transfer
            # approval = self.env['account.move.approval'].search([('name', '=', 'transfer_prepared'), ('limit', '<=', rec.amount_total)], order="limit desc", limit=1)
            rec.payment_transfer_prepared_domain = json.dumps([('id', 'in', rec._get_approval('transfer_prepared', rec.amount_total).approver.users.ids)])
            rec.payment_transfer_approver1_domain = json.dumps([('id', 'in', rec._get_approval('transfer_approver1', rec.amount_total).approver.users.ids)])
            rec.payment_transfer_approver2_domain = json.dumps([('id', 'in', rec._get_approval('transfer_approver2', rec.amount_total).approver.users.ids)])

    def _set_signed_id(self):
        self.ensure_one()
        self.signed_invoice_approval1_id = self._get_approval('transfer_prepared', self.amount_total).approver.users[0].id if len(self._get_approval('transfer_prepared', self.amount_total).approver.users) else False
        self.payment_transfer_approver1_id = self._get_approval('transfer_approver1', self.amount_total).approver.users[0].id if len(self._get_approval('transfer_approver1', self.amount_total).approver.users) else False
        self.payment_transfer_approver2_id = self._get_approval('transfer_approver2', self.amount_total).approver.users[0].id if len(self._get_approval('transfer_approver2', self.amount_total).approver.users) else False

    def get_employee(self, user_id):
        return self.env['hr.employee'].sudo().search([('user_id', '=', user_id)])

    @api.model
    def create(self, vals):
        res = super(AccountPayment, self).create(vals)
        res._set_signed_id()
        return res
