from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    partner_id = fields.Many2one('res.partner', domain="[('supplier_rank', '!=', 0)]")

    @api.model_create_multi
    def create(self, vals_list):
        orders = super(PurchaseOrder, self).create(vals_list)
        for order in orders:
            if '{VND}' in order.name:
                order.update({
                    'name': order.name.replace('{VND}', order.partner_id.name)
                })
        return orders

    def write(self, vals):
        partner_name = ''
        if 'partner_id' in vals:
            partner_name = self.partner_id.name
        res = super().write(vals)
        if 'partner_id' in vals:
            self.name = self.name.replace(partner_name, self.partner_id.name)
        return res
