from odoo import api, fields, models, _


class ResourceCalendarLeaves(models.Model):
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
    holiday_type = fields.Selection(
        selection=[
            ("public_holiday", "Public Holiday"),
            ("special_holiday", "Special Holiday"),
        ],
        string="Holiday Type",
    )
