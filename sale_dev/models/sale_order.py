# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_contact = fields.Char("Contact")
    start_date = fields.Date(string="Start Date", copy=False, required=True)
    loading_date = fields.Date(string="Loading Date", copy=False)
    commodity = fields.Char(string="Commodity")
    cargo = fields.Float(string="Cargo")
    grt = fields.Float(string="GRT")
    flag = fields.Char(string="Flag")
    no_bl = fields.Char(string="No. B/L")
    shipper = fields.Char(string="Shipper")
    mv = fields.Char(string="MV")

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
