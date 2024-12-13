from odoo import fields, models, api, _


class Employee(models.Model):
    _inherit = "hr.employee"

    employee_transfer_ids = fields.One2many('employee.transfer', 'employee_id', string="Status Alteration",
                                            domain=[('state', '=', 'done')])
