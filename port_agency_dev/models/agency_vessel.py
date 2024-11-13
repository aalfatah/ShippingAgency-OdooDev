# -- coding: utf-8 --

from odoo import api, fields, models, _


class Vessel(models.Model):
    _name = 'agency.vessel'
    _description = "Vessel"
    _order = "name"
    _inherit = ['mail.thread']

    name = fields.Char('Vessel')
    type = fields.Selection([('TB', 'Tugboat'), ('B', 'Barge')], string="Vessel Type")
    grt = fields.Float('GRT')
    capacity = fields.Float('Capacity')
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('vessel_unique', 'UNIQUE(name)', 'A vessel must be unique!'),
    ]
