from odoo import api, fields, models, _


class Employee(models.Model):
    _inherit = "hr.employee"

    travel_ids = fields.One2many('travel.request', 'employee_id', string='Travel')
