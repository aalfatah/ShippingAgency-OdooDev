# -*- coding: utf-8 -*-

from odoo import api, fields, models
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    disallow_multi_travel = fields.Boolean(string="Disallow Multiple Travel")
    pemberi_tugas_id = fields.Many2many('hr.employee', 'employee_pemberi_tugas', 'employee_id', 'pemberi_tugas',
                                        string='Pemberi Tugas')
    mengetahui_id = fields.Many2many('hr.employee', 'employee_mengetahui', 'employee_id', 'mengetahui',
                                     string='Mengetahui')
    declaration_reminder_1 = fields.Integer(string="First Reminder")
    declaration_reminder_2 = fields.Integer(string="Second Reminder")
    declaration_reminder_3 = fields.Integer(string="Third Reminder")
    declaration_reminder_user_id = fields.Many2many('res.users', 'reminder_user', 'user_id', 'reminder',
                                                    string='Cc Email Reminder')

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        config_parameters = self.env['ir.config_parameter']
        config_parameters.set_param("disallow_multi_travel", self.disallow_multi_travel)
        config_parameters.set_param("pemberi_tugas_id", self.pemberi_tugas_id.ids)
        config_parameters.set_param("mengetahui_id", self.mengetahui_id.ids)
        config_parameters.set_param('declaration_reminder_1', self.declaration_reminder_1)
        config_parameters.set_param('declaration_reminder_2', self.declaration_reminder_2)
        config_parameters.set_param('declaration_reminder_3', self.declaration_reminder_3)
        config_parameters.set_param("declaration_reminder_user_id", self.declaration_reminder_user_id.ids)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res['disallow_multi_travel'] = params.get_param('disallow_multi_travel', default=False)

        pemberi_tugas_ids = params.get_param('pemberi_tugas_id', default=False)
        res.update(pemberi_tugas_id=[(6, 0, literal_eval(pemberi_tugas_ids))] if pemberi_tugas_ids else False, )

        mengetahui_ids = params.get_param('mengetahui_id', default=False)
        res.update(mengetahui_id=[(6, 0, literal_eval(mengetahui_ids))] if mengetahui_ids else False, )

        res.update(declaration_reminder_1=int(params.get_param('declaration_reminder_1')))
        res.update(declaration_reminder_2=int(params.get_param('declaration_reminder_2')))
        res.update(declaration_reminder_3=int(params.get_param('declaration_reminder_3')))

        declaration_reminder_user_ids = params.get_param('declaration_reminder_user_id', default=False)
        res.update(declaration_reminder_user_id=[
            (6, 0, literal_eval(declaration_reminder_user_ids))] if declaration_reminder_user_ids else False, )

        return res
