from odoo import api, fields, models, _
import logging
import time
import csv
from odoo.modules import get_module_path
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class EfakturPartnerWizard(models.TransientModel):
    _name = 'efaktur.efaktur_partner'
    _description = 'eFaktur Partner Wizard'
    
    def confirm_button(self):
        """
        export partner yang is_efaktur_exported = False
        update setelah export
        :return: 
        """
        cr = self.env.cr

        headers = [
            'LT',
            'NPWP',
            'NAMA',
            'JALAN',
            'BLOK',
            'NOMOR',
            'RT',
            'RW',
            'KECAMATAN',
            'KELURAHAN',
            'KABUPATEN',
            'PROPINSI',
            'KODE_POS',
            'NOMOR_TELEPON'
        ]

        mpath = get_module_path('efaktur_dev')
        csvfile = open(mpath + '/static/partner.csv', 'w')
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow([h.upper() for h in headers])

        partner = self.env['res.partner']
        partners = partner.search([('is_efaktur_exported','=',False),
                                   ('npwp','!=',False)])
        i=0
        for part in partners:
            npwp = part.npwp.replace(".","").replace("-","")
            data = {
                'LT'        : 'LT',
                'NPWP'      : npwp,
                'NAMA'      : part.name,
                'JALAN'     : part.street or '',
                'BLOK'      : part.blok or '',
                'NOMOR'     : part.nomor or '',
                'RT'        : part.rt or '',
                'RW'        : part.rw or '',
                'KECAMATAN' : part.kecamatan_id.name or '',
                'KELURAHAN' : part.kelurahan_id.name or '',
                'KABUPATEN' : part.kecamatan_id.kota_id.name or '',
                'PROPINSI'  : part.state_id.name or '',
                'KODE_POS'  : part.zip or '',
                'NOMOR_TELEPON': part.phone or ''
            }
            csvwriter.writerow([data[v] for v in headers])

            part.is_efaktur_exported=True
            part.date_efaktur_exported=time.strftime("%Y-%m-%d %H:%M:%S")
            i+=1

        cr.commit()
        csvfile.close()

        raise UserError("Export %s record(s) Done!" % i)
