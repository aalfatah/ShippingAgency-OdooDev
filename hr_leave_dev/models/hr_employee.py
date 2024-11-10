from odoo import api, fields, models, _

class Employee(models.Model):
    _inherit = "hr.employee"

    leave_allocation_ids = fields.One2many('hr.employee.leave.allocation','employee_id', string="Leave Allocation")
