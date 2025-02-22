from odoo import _, api, fields, models


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    def approval_by(self, title):
        for request in self:
            employee = self.env['hr.employee'].sudo().search([('id', '=', request.requested_by.employee_id.parent_id.id)])
            if title == 'name':
                return employee.user_id.name
            elif title == 'job_title':
                return employee.job_id.name
            elif title == 'signature':
                return employee.user_id.signature
