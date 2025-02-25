from odoo import api, fields, models, _


class SyncRateCardWizard(models.TransientModel):
    _name = "sync.rate.card.wizard"
    _description = 'Sync Rate Card Wizard'

    order_id = fields.Many2one('sale.order', 'Sales Order')
    cost_structure_id = fields.Many2one('agency.cost.structure', 'Cost Structure From Rate Card',
                                        related='order_id.cost_structure_id')

    def sync_rate_card(self):
        self.order_id.sync_cost_structure()
        self.order_id.update_lines()
