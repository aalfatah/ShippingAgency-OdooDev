# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PayslipRun(models.Model):
    _name = "hr.payslip.run"
    _inherit = ["hr.payslip.run", "tier.validation"]
    _state_from = ["draft"]
    _state_to = ["close"]

    _tier_validation_manual_config = False
