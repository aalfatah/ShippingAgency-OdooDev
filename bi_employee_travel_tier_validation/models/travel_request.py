# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class TravelRequest(models.Model):
    _name = "travel.request"
    _inherit = ["travel.request", "tier.validation"]
    _state_from = ["draft"]
    _state_to = ["confirmed", "approved", "returned", "submitted"]

    _tier_validation_manual_config = False

    def validate_tier(self):
        super(TravelRequest, self).validate_tier()
        if not self.review_ids.filtered(lambda r: r.status != 'approved'):
            self.action_confirm()

    def get_approval(self, level, option):
        user_id = False
        if level == 1 and len(self.review_ids) >= 1:
            user_id = self.review_ids[0].done_by
        elif level == 2 and len(self.review_ids) >= 2:
            user_id = self.review_ids[1].done_by
        if user_id:
            employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', user_id.id)])
            if option == 'name':
                return employee_id.name
            elif option == 'job_title':
                return employee_id.job_title
            elif option == 'signature':
                return user_id.signature
        return False
