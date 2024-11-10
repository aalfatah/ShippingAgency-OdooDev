from odoo import models


class MassConfirmOvertime(models.TransientModel):
    _name = 'hr.overtime.confirm'
    _description = 'hr.overtime.confirm'

    def confirm_overtime(self):
        context = self._context
        record_ids = context.get('active_ids', [])
        for each in record_ids:
            overtime_id = self.env['hr.overtime'].search([('id', '=', each),('state', 'in', ['draft'])])
            if overtime_id:
                overtime_id.submit_to_f()


class MassApproveOvertime(models.TransientModel):
    _name = 'hr.overtime.approve'
    _description = 'hr.overtime.approve'

    def approve_overtime(self):
        context = self._context
        record_ids = context.get('active_ids', [])
        for each in record_ids:
            overtime_id = self.env['hr.overtime'].search([('id', '=', each),('state', 'in', ['f_approve'])])
            if overtime_id:
                overtime_id.approve()

class MassCancelOvertime(models.TransientModel):
    _name = 'hr.overtime.cancel'
    _description = 'hr.overtime.cancel'

    def cancel_overtime(self):
        context = self._context
        record_ids = context.get('active_ids', [])
        for each in record_ids:
            overtime_id = self.env['hr.overtime'].search([('id', '=', each),('state', 'not in', ['draft'])])
            if overtime_id:
                overtime_id.cancel()
