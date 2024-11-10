from odoo import api, fields, models, _


class HolidaysAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    date_from = fields.Date(string="Date From", readonly=False)
    date_to = fields.Date(string="Date To", readonly=False)

    _sql_constraints = [
        ('duration_check', "CHECK ( number_of_days = 0 )", "The number of days must be not 0."),
    ]
