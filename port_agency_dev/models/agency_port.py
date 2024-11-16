# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Port(models.Model):
    _name = "agency.port"
    _description = "Port"
    _order = "name"
    _inherit = ['mail.thread']
    _rec_name = 'complete_name'
    _parent_store = True

    name = fields.Char('Port Name', required=True, tracking=True)
    code = fields.Char("Port Code", tracking=True)
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', recursive=True, store=True)
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    parent_id = fields.Many2one('agency.port', string='Parent Port', index=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    child_ids = fields.One2many('agency.port', 'parent_id', string='Child Ports')
    color = fields.Integer('Color Index')
    parent_path = fields.Char(index=True, unaccent=False)
    master_port_id = fields.Many2one('agency.port', 'Master Port', compute='_compute_master_port_id', store=True)
    area_id = fields.Many2one('res.area', 'Area')

    _sql_constraints = [
        ('port_unique', 'UNIQUE(complete_name)', 'A port name must be unique!'),
    ]

    def name_get(self):
        if not self.env.context.get('hierarchical_naming', True):
            return [(record.id, record.name) for record in self]
        return super(Port, self).name_get()

    @api.model
    def name_create(self, name):
        return self.create({'name': name}).name_get()[0]

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for port in self:
            if port.parent_id:
                port.complete_name = '%s / %s' % (port.parent_id.complete_name, port.name)
            else:
                port.complete_name = port.name

    @api.depends('parent_path')
    def _compute_master_port_id(self):
        for port in self:
            port.master_port_id = False
            if port.parent_path:
                port.master_port_id = int(port.parent_path.split('/')[0])

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive ports.'))

    # @api.model_create_multi
    # def create(self, vals_list):
    #     # TDE note: auto-subscription of manager done by hand, because currently
    #     # the tracking allows to track+subscribe fields linked to a res.user record
    #     # An update of the limited behavior should come, but not currently done.
    #     ports = super(Port, self.with_context(mail_create_nosubscribe=True)).create(vals_list)
    #     # for port, vals in zip(ports, vals_list):
    #     #     manager = self.env['hr.employee'].browse(vals.get("manager_id"))
    #     #     if manager.user_id:
    #     #         port.message_subscribe(partner_ids=manager.user_id.partner_id.ids)
    #     return ports
    #
    # def write(self, vals):
    #     return super(Port, self).write(vals)
    #
    # def get_formview_action(self, access_uid=None):
    #     res = super().get_formview_action(access_uid=access_uid)
    #     if (not self.user_has_groups('hr.group_hr_user') and
    #        self.env.context.get('open_employees_kanban', False)):
    #         res.update({
    #             'name': self.name,
    #             'res_model': 'hr.employee.public',
    #             'view_type': 'kanban',
    #             'view_mode': 'kanban',
    #             'views': [(False, 'kanban'), (False, 'form')],
    #             'context': {'searchpanel_default_port_id': self.id},
    #             'res_id': False,
    #         })
    #     return res
    #
    # def get_children_port_ids(self):
    #     return self.env['agency.port'].search([('id', 'child_of', self.ids)])
