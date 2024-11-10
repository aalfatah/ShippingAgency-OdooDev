# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettingsovertime(models.TransientModel):
    _inherit = 'res.config.settings'

    # meal_hours = fields.Integer(string='Default hours to get meal allowance')
    wage_hours_python_compute = fields.Text(string='Python Code', default="result = (wage + tunjangan_transport)/173")
    # transport_division_month = fields.Integer(string='Default days transport division')
    break_hour_from = fields.Float(string="Break Hour From")
    break_hour_to = fields.Float(string="Break Hour To")
    period = fields.Selection([('last_month', 'Last Month'),('last_this_month', 'Last Month - This Month')], string='Period')
    payroll_period_from = fields.Integer(string='Start Date')

    def set_values(self):
        res = super(ResConfigSettingsovertime, self).set_values()
        config_parameters = self.env['ir.config_parameter']
        # config_parameters.set_param("meal_hours", self.meal_hours)
        config_parameters.set_param("wage_hours_python_compute", self.wage_hours_python_compute)
        # config_parameters.set_param("transport_division_month", self.transport_division_month)
        config_parameters.set_param("break_hour_from", self.break_hour_from)
        config_parameters.set_param("break_hour_to", self.break_hour_to)

        config_parameters.set_param("period", self.period)
        config_parameters.set_param("payroll_period_from", self.payroll_period_from)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettingsovertime, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            # meal_hours=params.get_param('meal_hours', default=False),
            wage_hours_python_compute = params.get_param('wage_hours_python_compute', default=False),
            # transport_division_month = params.get_param('transport_division_month', default=False),
            break_hour_from = params.get_param('break_hour_from', default=False),
            break_hour_to = params.get_param('break_hour_to', default=False),

            period = params.get_param('period', default=False),
            payroll_period_from = params.get_param('payroll_period_from', default=False),
        )
        return res



