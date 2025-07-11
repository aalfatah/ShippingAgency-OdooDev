# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_contact = fields.Char("Contact", tracking=True)
    start_date = fields.Date(string="Start Date", copy=False, required=True, tracking=True)
    loading_date = fields.Date(string="Loading Date", copy=False, tracking=True)
    commodity = fields.Char(string="Commodity", tracking=True)
    cargo = fields.Float(string="Cargo", tracking=True)
    grt = fields.Float(string="GRT",  tracking=True)
    flag = fields.Char(string="Flag", tracking=True)
    no_bl = fields.Char(string="No. B/L", tracking=True)
    shipper = fields.Char(string="Shipper", tracking=True)
    mv = fields.Char(string="MV", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New") and vals.get("type_id"):
                sale_type = self.env["sale.order.type"].browse(vals["type_id"])
                if sale_type.sequence_id:
                    vals["name"] = sale_type.sequence_id.with_context(ir_sequence_date=vals.get("start_date")).next_by_id(
                        sequence_date=vals.get("start_date")
                    )
        return super().create(vals_list)
    
    def write(self, vals):
        if 'start_date' in vals:
            if datetime.strptime(vals.get('start_date'), "%Y-%m-%d").month != self.start_date.month:
                raise UserError(_("Start date changes cannot be different months!"))
        return super(SaleOrder, self).write(vals)
