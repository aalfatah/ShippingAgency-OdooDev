from odoo import api, fields, models, tools, _


class HrSalaryRuleCategory(models.Model):
    _inherit = 'hr.salary.rule.category'
    _order = 'sequence'

    sequence = fields.Integer()


class HrSalaryRuleInherit(models.Model):
    _inherit = 'hr.salary.rule'

    appears_on_list = fields.Boolean(string="Appears on List Detail")
    bold_on_payslip = fields.Boolean(string="Bold on Payslip")
    show_zero_on_payslip = fields.Boolean(string="Show if 0 on Payslip")