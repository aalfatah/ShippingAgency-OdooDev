from odoo import fields, models, api, _


class Department(models.Model):
    _inherit = "hr.department"

    approval_director = fields.Boolean('Approval Director')
