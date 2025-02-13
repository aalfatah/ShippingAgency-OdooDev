# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import groupby


class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_id = fields.Many2one('sale.order', 'Sales Order', compute='_get_sale_order')
    po_no = fields.Char(string='No. PO', compute='_get_sale_order')
    vo_no = fields.Char(string='No. VO', compute='_get_sale_order')
    vessel_ids = fields.Many2many('agency.vessel', 'sale_order_vessel_rel', string='Vessel', compute='_get_sale_order')
    last_port_id = fields.Many2one('agency.port', string='Last Port', compute='_get_sale_order')
    load_port_ids = fields.Many2many('agency.port', 'sale_order_load_port_rel', string='Load Port',
                                     compute='_get_sale_order')
    discharge_port_ids = fields.Many2many('agency.port', 'sale_order_discharge_port_rel', string='Discharge Port',
                                          compute='_get_sale_order')

    def _get_sale_order(self):
        for move in self:
            sale_line_ids = move.line_ids.mapped('sale_line_ids')
            sale_id = sale_line_ids[0].order_id
            move.sale_id = sale_id.id
            move.po_no = sale_id.client_order_ref
            move.vo_no = sale_id.vo_no
            move.vessel_ids = sale_id.vessel_ids
            move.last_port_id = sale_id.last_port_id.id
            move.load_port_ids = sale_id.load_port_ids
            move.discharge_port_ids = sale_id.discharge_port_ids
