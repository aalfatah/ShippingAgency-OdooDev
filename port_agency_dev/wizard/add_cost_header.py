from odoo import models, fields


class CostHeader(models.TransientModel):
    _name = 'add.cost.header'
    _description = 'Add Cost Header'

    cost_structure_id = fields.Many2one('agency.cost.structure', 'Cost Structure')
    cost_header_ids = fields.Many2many('agency.cost.header', 'add_cost_header_rel', 'add_id', 'cost_header_id',
                                       'Cost Header')

    def add_cost_header(self):
        lines = []
        for header in self.cost_header_ids:
            for item in header.cost_item_ids:
                lines.append((0, 0, {
                    'header_id': header.id,
                    'item_id': item.id,
                }))
        self.cost_structure_id.update({'line_ids': lines})
