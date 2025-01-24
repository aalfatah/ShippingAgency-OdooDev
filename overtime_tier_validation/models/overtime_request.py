# Copyright 2019-2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models, fields
from odoo.exceptions import Warning


class overtime_request(models.Model):
    _name = "hr.overtime"
    _inherit = ["hr.overtime", "tier.validation"]
    _state_from = ["draft"]
    _state_to = ["f_approve"]

    _tier_validation_manual_config = False

    employee_approval_id = fields.Many2one('hr.employee', string='Employee Approval',
                                           compute='_compute_approval_id', store=True,
                                           readonly=False, states={'refused': [('readonly', True)],
                                                                   'f_approve': [('readonly', True)],
                                                                   'approved': [('readonly', True)]})
    approval_id = fields.Many2one('res.users', string='Approval', related='employee_approval_id.user_id', store=True)

    @api.depends('employee_id')
    def _compute_approval_id(self):
        for rec in self:
            employee_approval_id = False
            if rec.employee_id:
                if rec.employee_id.department_id.parent_id:
                    employee_approval_id = rec.employee_id.department_id.parent_id.manager_id
                else:
                    employee_approval_id = rec.employee_id.department_id.manager_id
            if employee_approval_id:
                rec.employee_approval_id = employee_approval_id.id
            else:
                rec.employee_approval_id = False

    # @api.model
    # def _get_under_validation_exceptions(self):
    #     res = super(overtime_request, self)._get_under_validation_exceptions()
    #     res.append("route_id")
    #     return res

    def validate_tier(self):
        super(overtime_request, self).validate_tier()
        if not self.review_ids.filtered(lambda l: l.status != 'approved'):
            self.submit_to_f()

    def request_validation(self):
        if not self.contract_id and (not self.sudo().employee_id.contract_id or self.sudo().employee_id.contract_id.state != 'open'):
            raise Warning('Karyawan %s tidak punya contract yang aktif, informasikan team HR !' % self.employee_id.name)
        return super(overtime_request, self).request_validation()

    # def get_spkl_approver(self):
    #     approved = []
    #     for review_id in self.review_ids:
    #         approved.append(review_id.status == 'approved')
    #     return approved
