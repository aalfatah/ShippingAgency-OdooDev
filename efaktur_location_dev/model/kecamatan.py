from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)


class Kecamatan(models.Model):
    _name = 'efaktur.kecamatan'
    _description = 'Kecamatan'

    name = fields.Char('Kecamatan', index=1)
    kota_id = fields.Many2one(comodel_name="efaktur.kota", string="Kota", required=False, )

