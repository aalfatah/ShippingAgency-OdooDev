from odoo import fields, models, _


class Partner(models.Model):
    _inherit = "res.partner"

    number = fields.Char(string="Number", index=True)

    _sql_constraints = [
        ('number_unique', 'unique (number)', 'Partner number already exists!'),
    ]