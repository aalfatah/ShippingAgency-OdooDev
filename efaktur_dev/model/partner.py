from odoo import api, fields, models, _


class Partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    is_efaktur_exported = fields.Boolean(string="Is eFaktur Exported",  )
    date_efaktur_exported = fields.Datetime(string="eFaktur Exported Date", required=False, )

    npwp = fields.Char(string="NPWP", required=False)
    blok = fields.Char(string="Blok", required=False)
    nomor = fields.Char(string="Nomor", required=False)
    rt = fields.Char(string="RT", required=False)
    rw = fields.Char(string="RW", required=False)

    _sql_constraints = [
        (
            "npwp_uniq",
            "unique (npwp)",
            "Partner NPWP duplicate!",
        )
    ]

    @api.depends("street","street2","city","state_id", "country_id","blok","nomor","rt","rw","kelurahan_id","kecamatan_id")
    def _alamat_lengkap(self):
        for partner in self:
            lengkap = partner.street or ""
            lengkap += " " + (partner.street2 or '')

            if partner.blok:
                lengkap += " Blok: " + partner.blok + ", "
            if partner.nomor:
                lengkap += " Nomor: " + partner.nomor + ", "

            if partner.rt:
                lengkap += " RT: " + partner.rt
            if partner.rw:
                lengkap += " RW: " + partner.rw

            if partner.kelurahan_id:
                lengkap += " Kel: " + partner.kelurahan_id.name + ","

            if partner.kecamatan_id:
                lengkap += " Kec: " + partner.kecamatan_id.name

            if partner.kota_id:
                lengkap += """
            """ + partner.kota_id.name + ","

            if partner.state_id:
                lengkap += " " + partner.state_id.name

            partner.alamat_lengkap = lengkap.upper()

    alamat_lengkap = fields.Char(string="Alamat Lengkap", required=False, compute="_alamat_lengkap")

