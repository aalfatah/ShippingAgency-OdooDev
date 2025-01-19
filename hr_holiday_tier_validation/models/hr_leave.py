# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class HolidaysRequest(models.Model):
    _name = "hr.leave"
    _inherit = ["hr.leave", "tier.validation"]
    _state_from = ["draft", "confirm"]
    _state_to = ["validate"]

    _tier_validation_manual_config = False

    employee_approval_id = fields.Many2one('hr.employee', string='Employee Approval',
                                           compute='_compute_approval_id', store=True,
                                           readonly=False, states={'cancel': [('readonly', True)],
                                                                   'refuse': [('readonly', True)],
                                                                   'validate1': [('readonly', True)],
                                                                   'validate': [('readonly', True)]})
    approval_id = fields.Many2one('res.users', string='Approval', related='employee_approval_id.user_id', store=True)

    @api.depends('employee_id')
    def _compute_approval_id(self):
        for holiday in self:
            employee_approval_id = False
            if holiday.employee_id:
                if holiday.employee_id.department_id.parent_id:
                    employee_approval_id = holiday.employee_id.department_id.parent_id.manager_id
                else:
                    employee_approval_id = holiday.employee_id.department_id.manager_id
            if employee_approval_id:
                holiday.employee_approval_id = employee_approval_id.id
            else:
                holiday.employee_approval_id = False

    def validate_tier(self):
        super(HolidaysRequest, self).validate_tier()
        if not any(self.review_ids.filtered(lambda r: r.status == "pending")):
            self.action_approve()
