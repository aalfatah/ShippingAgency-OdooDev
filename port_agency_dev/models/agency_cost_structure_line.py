from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class CostStructureLine(models.Model):
    _name = 'agency.cost.structure.line'
    _description = 'Cost Structure Line'
    _inherit = ['mail.thread']

    sequence = fields.Integer("Number")
    name = fields.Text(string="Description", compute='_compute_name', store=True, readonly=False, required=True,
                       precompute=True)
    display_type = fields.Selection([('line_section', "Section"), ('line_note', "Note")], default=False)
    cost_structure_id = fields.Many2one('agency.cost.structure', string="Cost Structure", ondelete='cascade')
    package_id = fields.Many2one('agency.cost.package', string="Package")
    header_id = fields.Many2one('agency.cost.header', string="Header")
    item_id = fields.Many2one('agency.cost.item', string="Item")
    code = fields.Char("Cost Code", related="item_id.code")
    standard_cost = fields.Float(string="Standard Cost", compute='_compute_standard_cost')
    quantity = fields.Float(string="Quantity", default=1)
    estimated_cost = fields.Float(string="Estimated Cost", compute='_compute_estimated_cost')

    @api.depends('item_id')
    def _compute_name(self):
        for line in self:
            if not line.item_id:
                continue
            line.name = "%s - %s" % (line.item_id.name, line.header_id.name)

    @api.depends('item_id', 'cost_structure_id.grt')
    def _compute_standard_cost(self):
        for row in self:
            row.standard_cost = 0
            if row.item_id and row.item_id.cost_formula:
                local_dict = {'PARENT': row.cost_structure_id} | self.other_cost(row.sequence)
                safe_eval(row.item_id.cost_formula, local_dict, mode="exec", nocopy=True)
                row.standard_cost = ('result' in local_dict) and local_dict['result'] or 0

    @api.depends('quantity')
    def _compute_estimated_cost(self):
        for row in self:
            row.estimated_cost = row.standard_cost * row.quantity

    def other_cost(self, sequence):
        cost_dict = {}
        for row in self.cost_structure_id.line_ids.filtered(lambda c: c.sequence < sequence and
                                                                      c.item_id.cost_formula != False):
            try:
                cost_dict[row.code] = row.standard_cost
            except Exception as e:
                continue
        return cost_dict
