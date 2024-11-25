from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class CostStructure(models.Model):
    _name = 'agency.cost.structure'
    _description = 'Cost Structure'
    _inherit = ['mail.thread']

    sequence = fields.Integer("Number", required=True, tracking=True)
    name = fields.Char(string='Code', required=True, copy=False, tracking=True, default='New')
    active = fields.Boolean('Active', default=True)
    vessel_ids = fields.Many2many('agency.vessel', 'agency_cost_structure_vessel_rel', 'cost_structure_id', 'vessel_id',
                                  string='Vessel', tracking=True)
    grt = fields.Float('GRT', compute='_get_vessel_grt', tracking=True)
    capacity = fields.Float('Capacity', tracking=True)
    last_port_id = fields.Many2one('agency.port', 'Last Port', tracking=True)
    load_port_ids = fields.Many2many('agency.port', 'agency_cost_structure_load_port_rel', 'cost_structure_id',
                                     'port_id', 'Load Port', tracking=True)
    discharge_port_ids = fields.Many2many('agency.port', 'agency_cost_structure_discharge_port_rel',
                                          'cost_structure_id', 'port_id', 'Discharge Port', tracking=True)
    amount_total = fields.Float(string="Total", compute='_compute_total')
    line_ids = fields.One2many('agency.cost.structure.line', 'cost_structure_id', 'Lines', copy=True)

    @api.onchange('vessel_ids')
    def _get_vessel_grt(self):
        for s in self:
            s.grt = sum(s.vessel_ids.mapped('grt')) if s.vessel_ids else 0

    @api.onchange('line_ids')
    def _compute_total(self):
        for s in self:
            s.amount_total = sum(s.line_ids.mapped('estimated_cost')) if s.line_ids else 0

    # @api.model_create_multi
    # def create(self, vals):
    #     lines = super(CostStructure, self).create(vals)
    #     for line in lines:
    #         msg = f"A new cost line with the name {line.name} has been added."
    #         line.cost_structure_id.message_post(body=msg)

    def write(self, vals):
        msg = ''
        if 'vessel_ids' in vals:
            msg = f"<li>Vessel: %s -> %s</li>" % \
                  (', '.join(self.env['agency.vessel'].browse(v).name for v in self.vessel_ids.ids),
                   ', '.join(self.env['agency.vessel'].browse(v).name for v in vals.get('vessel_ids')[0][2]))
            msg += f"<li>GRT: %s -> %s</li>" % \
                   ('{0:,.2f}'.format(self.grt),
                    '{0:,.2f}'.format(sum(self.env['agency.vessel'].browse(v).grt for v in
                                          vals.get('vessel_ids')[0][2])))
        if 'load_port_ids' in vals:
            msg += f"<li>Load Port: %s -> %s</li>" % \
                   (', '.join(self.env['agency.port'].browse(v).complete_name for v in self.load_port_ids.ids),
                    ', '.join(self.env['agency.port'].browse(v).complete_name for v in vals.get('load_port_ids')[0][2]))
        if 'discharge_port_ids' in vals:
            msg += f"<li>Discharge Port: %s -> %s</li>" % \
                   (', '.join(self.env['agency.port'].browse(v).complete_name for v in self.discharge_port_ids.ids),
                    ', '.join(self.env['agency.port'].browse(v).complete_name for v in
                              vals.get('discharge_port_ids')[0][2]))
        if msg:
            self.message_post(body=msg)
        return super(CostStructure, self).write(vals)
