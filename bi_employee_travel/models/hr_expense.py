# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class Expense(models.Model):
    _inherit = "hr.expense"

    travel_id = fields.Many2one('travel.request', 'Travel Cash Advance')
    travel_expense_id = fields.Many2one('travel.request', 'Travel Expense')
