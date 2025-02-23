# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class TravelRequest(models.Model):
    _name = "travel.request"
    _inherit = ["travel.request", "tier.validation"]
    _state_from = ["confirmed"]
    _state_to = ["approved", "returned", "submitted"]

    _tier_validation_manual_config = False
