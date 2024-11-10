# coding: utf-8
from odoo import api, fields, models
from datetime import datetime, timedelta


class HrPayrollOtherInputLineKamaju(models.Model):
    _inherit = 'hr.payroll.other.input.line'
    
    description = fields.Char(string="Description")

