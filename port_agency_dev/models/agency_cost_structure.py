from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class CostStructure(models.Model):
    _name = 'agency.cost.structure'
    _description = 'Cost Structure'
    _inherit = ['mail.thread']

    sequence = fields.Integer("Number", required=True, tracking=True)
    name = fields.Char(string='Code', required=True, copy=False, tracking=True)
    active = fields.Boolean('Active', default=True)
    vessel_ids = fields.Many2many('agency.vessel', 'agency_cost_structure_vessel_rel', 'cost_structure_id', 'vessel_id',
                                  string='Vessel')
    grt = fields.Float('GRT', compute='_get_vessel_grt')
    capacity = fields.Float('Capacity', tracking=True)
    last_port_id = fields.Many2one('agency.port', 'Last Port', tracking=True)
    load_port_ids = fields.Many2many('agency.port', 'agency_cost_structure_load_port_rel', 'cost_structure_id',
                                     'port_id', 'Load Port', tracking=True)
    discharge_port_ids = fields.Many2many('agency.port', 'agency_cost_structure_discharge_port_rel',
                                          'cost_structure_id', 'port_id', 'Discharge Port', tracking=True)
    line_ids = fields.One2many('agency.cost.structure.line', 'cost_structure_id', 'Lines')

    @api.onchange('vessel_ids')
    def _get_vessel_grt(self):
        for s in self:
            s.grt = sum(s.vessel_ids.mapped('grt')) if s.vessel_ids else 0
