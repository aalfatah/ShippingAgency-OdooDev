from odoo import api, fields, models, _


class ResourceCalendarLeavesDev(models.Model):
    _inherit = "resource.calendar.leaves"

    religion = fields.Selection(
        selection=[
            ("islam", "Islam"),
            ("kristen", "Kristen, Katholik"),
            ("hindu", "Hindu"),
            ("buddha", "Buddha"),
            ("konghucu", "Konghucu"),
        ],
        string="Religion",
    )

