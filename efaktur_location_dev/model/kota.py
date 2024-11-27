from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)


class Kota(models.Model):
    _name = 'efaktur.kota'
    _description = 'Kota'

    name = fields.Char('Kota/Kab', index=1)
    jenis = fields.Selection(string="Jenis", selection=[('kota', 'Kota'), ('kab', 'Kab.'), ], required=False, index=1)
    state_id = fields.Many2one(comodel_name="res.country.state", string="State", required=False, )

