from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)


class Kelurahan(models.Model):
    _name = 'efaktur.kelurahan'
    _description = 'Kelurahan'

    name = fields.Char('Kelurahan')
    zip = fields.Integer(string="Kode POS", required=False, )
    kecamatan_id = fields.Many2one(comodel_name="efaktur.kecamatan", string="Kecamatan", required=False, )
