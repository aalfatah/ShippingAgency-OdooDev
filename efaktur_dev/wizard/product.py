from odoo import api, fields, models, _
import time
import csv
from odoo.modules import get_module_path
from odoo.exceptions import UserError


class EfakturProductWizard(models.TransientModel):
    _name = 'efaktur.efaktur_product'
    _description = 'eFaktur Product Wizard'

    def confirm_button(self):
        """
        export product yang is_efaktur_exported = False
        update setelah export
        :return: 
        """
        cr = self.env.cr

        headers = [
            'OB',
            'KODE_OBJEK',
            'NAMA',
            'HARGA_SATUAN'
        ]

        mpath = get_module_path('efaktur_dev')
        csvfile = open(mpath + '/static/product.csv', 'w')
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow([h.upper() for h in headers])

        product = self.env['product.template']
        products = product.search([('is_efaktur_exported','=',False)])
        i=0
        for prod in products:
            data = {
                'OB'        : 'OB',
                'KODE_OBJEK': prod.default_code or '',
                'NAMA'      : prod.name,
                'HARGA_SATUAN':prod.list_price
            }
            try:
                csvwriter.writerow([data[v] for v in headers])
            except Exception as e:
                print('=========================',e)

            prod.is_efaktur_exported=True
            prod.date_efaktur_exported=time.strftime("%Y-%m-%d %H:%M:%S")
            i += 1

        cr.commit()
        csvfile.close()

        raise UserError("Export %s record(s) Done!" % i)
