from odoo import _, api, fields, models


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    def approval_by(self, title, level=1):
        """
        Get approval info (name, job title, or signature) from the employee's hierarchy.
        
        :param str title: 'name', 'job_title', or 'signature'
        :param int level: 1 for parent (direct manager), 2 for grandparent (manager's manager)
        :return: Requested information or False if not found
        """
        self.ensure_one()
        
        if not self.requested_by.employee_id:
            return False
        
        employee = self.requested_by.employee_id
        
        # hierarki berdasarkan level
        for _ in range(level):
            if not employee.parent_id:
                return False  # jika tidak ada parent high-level
            employee = employee.parent_id
        
        if title == 'name':
            return employee.user_id.name if employee.user_id else False
        elif title == 'job_title':
            return employee.job_id.name if employee.job_id else False
        elif title == 'signature':
            return employee.user_id.signature if employee.user_id else False
        return False