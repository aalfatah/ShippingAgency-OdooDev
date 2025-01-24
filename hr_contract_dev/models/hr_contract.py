# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class Contract(models.Model):
    _inherit = 'hr.contract'

    wage = fields.Monetary('Wage', required=True, tracking=True, help="Employee's monthly gross wage.",
                           groups='hr_payroll_community.group_hr_payroll_community_user')
    contract_wage = fields.Monetary('Contract Wage', compute='_compute_contract_wage',
                                    groups='hr_payroll_community.group_hr_payroll_community_user')
