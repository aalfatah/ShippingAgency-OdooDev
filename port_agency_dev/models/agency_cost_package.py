# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class CostPackage(models.Model):
    _name = 'agency.cost.package'
    _description = 'Cost Packages'

    sequence = fields.Integer("Number", required=True, )
    name = fields.Char("Work Package Name", required=True, )

    _sql_constraints = [
        ('port_unique', 'UNIQUE(name)', 'A work package must be unique!'),
    ]