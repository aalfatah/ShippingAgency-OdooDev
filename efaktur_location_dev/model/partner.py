from odoo import api, fields, models, _
import time
import logging
_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    # after zip
    kelurahan_id = fields.Many2one(comodel_name="efaktur.kelurahan", string="Kelurahan", required=False, )
    kecamatan_id = fields.Many2one(comodel_name="efaktur.kecamatan", string="Kecamatan", required=False, )
    kota_id = fields.Many2one(comodel_name="efaktur.kota", string="Kota/Kab", required=False, )

