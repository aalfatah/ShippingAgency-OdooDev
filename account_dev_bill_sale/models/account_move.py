import logging
from odoo import fields, models, api

try:
    from num2words import num2words
except ImportError:
    logging.getLogger(__name__).warning(
        "The num2words python library is not installed."
    )
    num2words = None


class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_order_id = fields.Many2one('sale.order', compute='_origin_sale_order_id')

    def sale_order_customer_contact(self):
        if self.sale_order_id:
            return self.sale_order_id.customer_contact
        return False

    @api.depends('line_ids.sale_line_ids')
    def _origin_sale_order_id(self):
        for move in self:
            if move.line_ids.sale_line_ids:
                move.sale_order_id = move.line_ids.sale_line_ids.order_id[0]
            else:
                move.sale_order_id = False

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

    def total_amount_in_words(self):
        return num2words(int(self.amount_total), lang="id").title() + ' Rupiah'

    def invoice_signature(self):
        return self.sudo().env['res.users'].search([('id', '=', 13)]).signature

    def invoice_signature_name(self):
        return 'NURMIATI'
