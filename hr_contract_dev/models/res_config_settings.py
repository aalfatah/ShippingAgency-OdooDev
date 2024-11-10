# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # contract_monitoring_user_ids = fields.Many2many('hr.employee', string='Users to Monitoring Contract',related="company_id.contract_monitoring_user_ids", readonly=False)
    # contract_monitoring_mail_template_id = fields.Many2one('mail.template', 'Email Template', domain="[('model', '=', 'hr.contract')]", related="company_id.contract_monitoring_mail_template_id", readonly=False)
    contract_monitoring_mail_template_id = fields.Many2one('mail.template', 'Email Template', domain="[('model', '=', 'hr.employee')]")

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        config_parameters = self.env['ir.config_parameter']
        config_parameters.set_param("contract_monitoring_mail_template_id", self.contract_monitoring_mail_template_id.id)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            contract_monitoring_mail_template_id = int(params.get_param('contract_monitoring_mail_template_id', default=False)),
        )
        return res

# class Company(models.Model):
#     _inherit = "res.company"
#
#     # contract_monitoring_user_ids = fields.Many2many('hr.employee',string='Users to Monitoring Contract')
#     contract_monitoring_mail_template_id = fields.Many2one('mail.template', 'Email Template')
