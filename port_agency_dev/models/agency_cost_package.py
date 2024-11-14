# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class CostPackage(models.Model):
    _name = 'agency.cost.package'
    _description = 'Cost Packages'
    _inherit = ['mail.thread']

    sequence = fields.Integer("Number", required=True, tracking=True)
    name = fields.Char("Work Package Name", required=True, tracking=True)
    active = fields.Boolean('Active', default=True, tracking=True)

    _sql_constraints = [
        ('port_unique', 'UNIQUE(name)', 'A work package must be unique!'),
    ]