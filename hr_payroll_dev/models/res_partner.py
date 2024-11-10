from odoo import fields, models, _


class Partner(models.Model):
    _inherit = "res.partner"

    bpjstk_no = fields.Char(string='BPJS Ketenagakerjaan')
    bpjsks_no = fields.Char(string='BPJS Kesehatan')

    _sql_constraints = [
        ('bpjstk_uniq', 'unique(bpjstk_no)', "BPJS Ketenagakerjaan tidak boleh duplikat"),
        ('bpjsks_uniq', 'unique(bpjsks_no)', "BPJS Kesehatan tidak boleh duplikat"),
    ]
