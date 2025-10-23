# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import groupby


class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_id = fields.Many2one('sale.order', 'Sales Order', compute='_get_sale_order')
    no_bl = fields.Char(string="No. B/L", compute='_get_sale_order')
    vessel_ids = fields.Many2many('agency.vessel', 'sale_order_vessel_rel', string='Vessel', compute='_get_sale_order')
    vessel_name = fields.Char(string='Vessel Name', related='sale_id.vessel_name')
    last_port_id = fields.Many2one('agency.port', string='Last Port', compute='_get_sale_order')
    load_port_ids = fields.Many2many('agency.port', 'sale_order_load_port_rel', string='Load Port',
                                     compute='_get_sale_order')
    discharge_port_ids = fields.Many2many('agency.port', 'sale_order_discharge_port_rel', string='Discharge Port',
                                          compute='_get_sale_order')
    po_no = fields.Char(string='No. PO', store=True, readonly=True,
        states={
            'draft': [('readonly', False)]
        }
    )

    vo_no = fields.Char(string='No. VO', store=True, readonly=True,
        states={
            'draft': [('readonly', False)]
        }
    )

    po_date = fields.Date(string='Tanggal PO', store=True, readonly=True,
        states={
            'draft': [('readonly', False)]
        }
    )

    def _get_sale_order(self):
        for move in self:
            sale_id = False
            po_no = False
            vo_no = False
            po_date = False
            no_bl = False
            vessel_ids = False
            last_port_id = False
            load_port_ids = False
            discharge_port_ids = False
            sale_line_ids = move.line_ids.mapped('sale_line_ids')
            if sale_line_ids:
                sale = sale_line_ids[0].order_id
                sale_id = sale.id
                no_bl = sale.no_bl
                vessel_ids = sale.vessel_ids
                last_port_id = sale.last_port_id.id
                load_port_ids = sale.load_port_ids
                discharge_port_ids = sale.discharge_port_ids

                if not move.po_no and sale.client_order_ref:
                    move.po_no = sale.client_order_ref
                if not move.vo_no and sale.vo_no:
                    move.vo_no = sale.vo_no
                if not move.po_date and sale.po_date:
                    move.po_date = sale.po_date

            move.sale_id = sale_id
            move.no_bl = no_bl
            move.vessel_ids = vessel_ids
            move.last_port_id = last_port_id
            move.load_port_ids = load_port_ids
            move.discharge_port_ids = discharge_port_ids
