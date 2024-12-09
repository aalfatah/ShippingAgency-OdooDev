from odoo import fields, models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    sale_id = fields.Many2one('sale.order', 'Sales Order', tracking=True, ondelete='restrict')
    work_period = fields.Char('Perioda Kegiatan', compute='_work_period')

    @api.onchange('sale_id')
    def _work_period(self):
        for line in self:
            if line.sale_id:
                commitment_date = line.sale_id.commitment_date.date() if line.sale_id.commitment_date else False
                line.work_period = '%s - %s' % (line.sale_id.start_date or '', commitment_date or '')
            else:
                line.work_period = False

    @api.onchange('sale_id')
    def _onchange_sale_id(self):
        if self.sale_id and self.sale_id.vessel_ids:
            self.update({
                'name': '/'.join(v.name for v in self.sale_id.vessel_ids),
                'analytic_distribution': {self.sale_id.analytic_account_id.id: 100}
            })
