# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_contact = fields.Char("Contact")
    start_date = fields.Date(string="Start Date", copy=False)
    loading_date = fields.Date(string="Loading Date", copy=False)
    commodity = fields.Char(string="Commodity")
    cargo = fields.Float(string="Cargo")
    grt = fields.Float(string="GRT")
    flag = fields.Char(string="Flag")
