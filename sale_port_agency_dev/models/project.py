# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, _lt


class Project(models.Model):
    _inherit = 'project.project'

    # allow_billable = fields.Boolean("Billable")
    # sale_line_id = fields.Many2one(
    #     'sale.order.line', 'Sales Order Item', copy=False,
    #     compute="_compute_sale_line_id", store=True, readonly=False, index='btree_not_null',
    #     domain=lambda self: str(self._domain_sale_line_id()),
    #     help="Sales order item that will be selected by default on the tasks and timesheets of this project,"
    #         " except if the employee set on the timesheets is explicitely linked to another sales order item on the project.\n"
    #         "It can be modified on each task and timesheet entry individually if necessary.")
    # sale_order_id = fields.Many2one(string='Sales Order', related='sale_line_id.order_id', help="Sales order to which the project is linked.")
    # has_any_so_to_invoice = fields.Boolean('Has SO to Invoice', compute='_compute_has_any_so_to_invoice')
    # sale_order_count = fields.Integer(compute='_compute_sale_order_count', groups='sales_team.group_sale_salesman')
    # has_any_so_with_nothing_to_invoice = fields.Boolean('Has a SO with an invoice status of No', compute='_compute_has_any_so_with_nothing_to_invoice')
    # invoice_count = fields.Integer(compute='_compute_invoice_count', groups='account.group_account_readonly')
    # vendor_bill_count = fields.Integer(related='analytic_account_id.vendor_bill_count', groups='account.group_account_readonly')

    cost_structure_count = fields.Integer('Cost Structure', compute='_count_cost_structure')

    def _count_cost_structure(self):
        for project in self:
            project.cost_structure_count = len(project.sale_order_id.sale_cost_structure_line_ids)

    def action_show_cost_structure(self):
        action = self.env['ir.actions.act_window']._for_xml_id('sale_port_agency_dev.act_sale_open_cost_structure_view')
        action['display_name'] = _("Cost Structure %(name)s", name=self.name)
        action['domain'] = [('sale_order_id', '=', self.sale_order_id.id)]
        return action
