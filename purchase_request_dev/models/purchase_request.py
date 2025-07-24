from odoo import _, api, fields, models


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    def approval_by(self, title, level=1):
        
        self.ensure_one()
        
        if not self.requested_by.employee_id:
            return False
        
        employee = self.requested_by.employee_id
        
        # hierarki berdasarkan level
        for _ in range(level):
            if not employee.parent_id:
                return False
            employee = employee.parent_id
        
        if title == 'name':
            return employee.user_id.name if employee.user_id else False
        elif title == 'job_title':
            return employee.job_id.name if employee.job_id else False
        elif title == 'signature':
            return employee.user_id.signature if employee.user_id else False
        return False

    # def approval_by(self, title):
    #     for request in self:
    #         employee = self.env['hr.employee'].sudo().search([('id', '=', request.requested_by.employee_id.parent_id.id)])
    #         if title == 'name':
    #             return employee.user_id.name
    #         elif title == 'job_title':
    #             return employee.job_id.name
    #         elif title == 'signature':
    #             return employee.user_id.signature
    