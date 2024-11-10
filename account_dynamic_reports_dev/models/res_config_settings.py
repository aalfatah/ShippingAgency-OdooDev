# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    show_signer = fields.Boolean(string='Show Signer')
    accounting_staff_id = fields.Many2one('hr.employee', string='Accounting Staff')
    fatt_dept_head_id = fields.Many2one('hr.employee', string='FATT Dept. Head')
    fatt_director_id = fields.Many2one('hr.employee', string='FATT Director')
    presiden_director_id = fields.Many2one('hr.employee', string='Presiden Director')

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        config_parameters = self.env['ir.config_parameter']
        config_parameters.set_param("show_signer", self.show_signer)
        config_parameters.set_param("accounting_staff_id", self.accounting_staff_id.id)
        config_parameters.set_param("fatt_dept_head_id", self.fatt_dept_head_id.id)
        config_parameters.set_param("fatt_director_id", self.fatt_director_id.id)
        config_parameters.set_param("presiden_director_id", self.presiden_director_id.id)

        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res['show_signer'] = params.get_param('show_signer', default=False)

        accounting_staff_id = params.get_param('accounting_staff_id', default=False)
        if accounting_staff_id:
            res['accounting_staff_id'] = self.env['hr.employee'].sudo().browse(int(accounting_staff_id))
        fatt_dept_head_id = params.get_param('fatt_dept_head_id', default=False)
        if fatt_dept_head_id:
                res['fatt_dept_head_id'] = self.env['hr.employee'].sudo().browse(int(fatt_dept_head_id))
        fatt_director_id = params.get_param('fatt_director_id', default=False)
        if fatt_director_id:
            res['fatt_director_id'] = self.env['hr.employee'].sudo().browse(int(fatt_director_id))
        presiden_director_id = params.get_param('presiden_director_id', default=False)
        if presiden_director_id:
            res['presiden_director_id'] = self.env['hr.employee'].sudo().browse(int(presiden_director_id))

        return res

