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
    product_id = fields.Many2one("product.product", string="Product", related="item_id.product_id")
    standard_cost = fields.Float(string="Standard Cost", compute='compute_standard_cost')
    quantity = fields.Float(string="Quantity", default=1)
    estimated_cost = fields.Float(string="Estimated Cost", compute='compute_estimated_cost')
    allow_expense = fields.Boolean('Allow Expense')

    @api.onchange('item_id', 'package_id')
    def _set_allow_expense(self):
        for line in self:
            line.allow_expense = line.package_id.allow_expense

    @api.depends('item_id')
    def _compute_name(self):
        for line in self:
            if not line.item_id:
                continue
            line.name = "%s - %s" % (line.item_id.name, line.header_id.name)

    @api.depends('item_id', 'cost_structure_id.grt')
    def compute_standard_cost(self):
        for row in self:
            row.standard_cost = 0
            if row.item_id and row.item_id.cost_formula:
                local_dict = {'PARENT': row.cost_structure_id} | self.other_cost(row.sequence)
                safe_eval(row.item_id.cost_formula, local_dict, mode="exec", nocopy=True)
                row.standard_cost = ('result' in local_dict) and local_dict['result'] or 0
                row.compute_estimated_cost()

    @api.depends('quantity')
    def compute_estimated_cost(self):
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

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            item_id = self.env['agency.cost.item'].browse(val['item_id'])
            header_id = self.env['agency.cost.header'].browse(val['header_id'])
            item = self.env['agency.cost.item'].search([('cost_header_id', '=', header_id.id),
                                                        ('name', '=', item_id.name)])
            if not item:
                raise UserError(_("%s. Tidak ada cost item %s di cost header %s!" % (val['sequence'], item_id.name,
                                                                                     header_id.name)))
            if len(item) > 1:
                raise UserError(_("%s. Multiple cost item %s di cost header %s!" % (val['sequence'], item_id.name,
                                                                                    header_id.name)))
            val['item_id'] = item.id
        lines = super(CostStructureLine, self).create(vals)
        for line in lines:
            msg = f"A new cost line with the name {line.name} has been added."
            line.cost_structure_id.message_post(body=msg)

    def write(self, vals):
        if not ('estimated_cost' in vals and len(vals) == 1):
            self._log_line_tracking(vals)
        return super(CostStructureLine, self).write(vals)

    def _log_line_tracking(self, vals):
        template_id = 'port_agency_dev.track_cost_structure_template'
        for line in self:
            data = {}
            data.update({'name': line.name})
            if 'name' in vals:
                data.update({'new_name': vals.get('name')})
            if 'standard_cost' in vals:
                data.update({'standard_cost': vals.get('standard_cost')})
            if 'quantity' in vals:
                data.update({'quantity': vals.get('quantity')})
            if data:
                line.cost_structure_id.message_post_with_view(template_id, values={'line': line, 'data': data})
