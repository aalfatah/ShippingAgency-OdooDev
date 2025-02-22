from odoo import fields, models, api, _


class Job(models.Model):
    _inherit = "hr.job"

    approval_level = fields.Selection([('1 Level', '1 Level'),('2 Level', '2 Level')], 'Approval Level')
