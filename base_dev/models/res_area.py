from odoo import fields, models, _


class Area(models.Model):
    _name = 'res.area'
    _description = 'Area'

    name = fields.Char(string='Area')
    code = fields.Char(string="Kode")

    _sql_constraints = [
        ('area_uniq', 'unique (name)', 'Area already exists!'),
        ('code_uniq', 'unique (code)', "Kode area tidak boleh duplikat"),
    ]