from odoo import api, fields, models, _

class HolidaysType(models.Model):
    _inherit = "hr.leave.type"

    validity_by = fields.Selection(selection=[('type', 'Type'),('allocation', 'Allocation')])
    allocation_by = fields.Selection(selection=[('first', 'First Contract Date'),('permanent', 'Permanent Date')])
    initiate_leave_quota = fields.Boolean(string="Initiate Quota")
    leave_quota = fields.Integer("Leave Quota")
    # auto_generate_allocation = fields.Boolean(string="Create Allocation")
    validity_interval = fields.Integer(string='Interval')
    repeated_frequency = fields.Integer(string='Repeate Every')
