from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    def month_translate(self, month):
        return ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli',
                'Agustus', 'September', 'Oktober', 'November', 'Desember'][month - 1]

    def date_id(self):
        return self.invoice_date and "%s %s %s" % (self.invoice_date.day,
                                                   self.month_translate(self.invoice_date.month),
                                                   self.invoice_date.year) or ''

    def due_date_id(self):
        return self.invoice_date_due and "%s %s %s" % (self.invoice_date_due.day,
                                                       self.month_translate(self.invoice_date_due.month),
                                                       self.invoice_date_due.year) or ''
