# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class TravelExpense(models.Model):
    _name = "travel.expense"
    _description = "Travel Expense"

    product_id = fields.Many2one('product.product', string="Product", domain=[('can_be_expensed', '=', True)],
                                 required=True)
    unit_price = fields.Float(string="Unit Price", required=True)
    product_qty = fields.Float(string="Quantity", required=True)
    name = fields.Char(string="Expense Note")
    currency_id = fields.Many2one('res.currency', string="Currency")
