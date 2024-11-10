from odoo import api, fields, models, tools, _


class HrSalaryRuleCategory(models.Model):
    _inherit = 'hr.salary.rule.category'
    _order = 'sequence'

    sequence = fields.Integer()


class HrSalaryRuleInherit(models.Model):
    _inherit = 'hr.salary.rule'

    bold_on_payslip = fields.Boolean(string="Bold on Payslip")
