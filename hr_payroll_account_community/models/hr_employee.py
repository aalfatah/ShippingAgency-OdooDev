# -*- coding:utf-8 -*-

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee'

    salary_group_id = fields.Many2one('hr.salary.group', string='Salary Group', ondelete="restrict")
