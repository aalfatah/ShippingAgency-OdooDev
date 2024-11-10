from odoo import api, fields, models, _


class TravelType(models.Model):
    _name = "travel.type"
    _description = "Travel Type"

    name = fields.Char(string="Name", required=True)
    # claimable = fields.Boolean(string="Claimable")
    # show_leave = fields.Boolean(string="Show Leave")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Travel type sudah ada!"),
    ]
