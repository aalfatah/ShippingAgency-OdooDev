from odoo import fields, models, _


class Partner(models.Model):
    _inherit = "res.partner"

    identification_id = fields.Char(string="Identification No")

    _sql_constraints = [
        ('identification_unique', 'unique (identification_id)', "Identification number already exists!"),
    ]