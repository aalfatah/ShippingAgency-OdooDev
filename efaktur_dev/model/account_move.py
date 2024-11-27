from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    efaktur_id  = fields.Many2one(comodel_name="efaktur.efaktur", string="Nomor FP", required=False, )
    is_efaktur_exported = fields.Boolean(string="Is eFaktur Exported",  )
    date_efaktur_exported = fields.Datetime(string="eFaktur Exported Date", required=False, )

    masa_pajak = fields.Char(string="Masa Pajak", required=False, compute="_masa_pajak" )
    tahun_pajak = fields.Char(string="Tahun Pajak", required=False, compute="_tahun_pajak")

    efaktur_masukan = fields.Char(string="Nomor FP Masukan", required=False, )
    efaktur_jenis_transaksi = fields.Selection([('01','01'),('02','02'),('03','03'),('04','04'),('05','05'),('06','06'),('07','07'),('08','08'),('09','09')], string='Jenis Transaksi', default='01')
    efaktur_kode_pengganti = fields.Selection([('0','0'),('1','1')], string='Kode Pengganti', default='0')

    @api.depends("invoice_date")
    def _masa_pajak(self):
        for inv in self:
            if inv.invoice_date:
                d = inv.invoice_date.strftime("%m")
                inv.masa_pajak = d
            else:
                inv.masa_pajak = ''

    @api.depends("invoice_date")
    def _tahun_pajak(self):
        for inv in self:
            if inv.invoice_date:
                d = inv.invoice_date.strftime("%Y")
                inv.tahun_pajak = d
            else:
                inv.tahun_pajak = ''

    def action_invoice_open(self):
        res = super(AccountMove, self).action_invoice_open()
        self.is_efaktur_exported=False
        return res

    @api.model_create_multi
    def create(self, vals):
        if 'efaktur_id' in vals:
            if any(self.env['account.move'].sudo().search([('efaktur_id','=',vals['efaktur_id'])])):
                raise UserError(_('Nomor Seri Faktur Pajak sudah digunakan.'))
        return super(AccountMove, self).create(vals)

    def write(self, vals):
        if 'efaktur_id' in vals:
            if vals.get('efaktur_id') and any(self.env['account.move'].sudo().search([('efaktur_id','=',vals['efaktur_id'])])):
                raise UserError(_('Nomor Seri Faktur Pajak sudah digunakan.'))
        return super(AccountMove, self).write(vals)
