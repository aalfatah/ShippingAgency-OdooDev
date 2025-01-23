from odoo import models,fields,api
# from odoo.tools.translate import translate
# from pytz import timezone


class OvertimeRequestApproval(models.TransientModel):
    _name = 'hr.overtime.request.approval'
    _description = 'Overtime Request Approval'

    def submit(self):
        context = self._context
        record_ids = context.get('active_ids', [])
        for rec in record_ids:
            overtime_id = self.env['hr.overtime'].search([('id', '=', rec),('state', 'in', ['draft'])])
            if overtime_id:
                overtime_id.request_validation()


class OvertimeRestartApproval(models.TransientModel):
    _name = 'hr.overtime.restart.approval'
    _description = 'Overtime Restart Approval'

    def submit(self):
        context = self._context
        record_ids = context.get('active_ids', [])
        for rec in record_ids:
            overtime_id = self.env['hr.overtime'].search([('id', '=', rec),('state', 'in', ['draft'])])
            if overtime_id:
                overtime_id.restart_validation()


class OvertimeValidateTier(models.TransientModel):
    _name = 'hr.overtime.validate.tier'
    _description = 'Overtime Validate Tier'

    def submit(self):
        context = self._context
        record_ids = context.get('active_ids', [])
        for rec in record_ids:
            overtime_id = self.env['hr.overtime'].search([('id', '=', rec),('state', 'in', ['draft'])])
            if overtime_id:
                overtime_id.validate_tier()


class OvertimeRejectTier(models.TransientModel):
    _name = 'hr.overtime.reject.tier'
    _description = 'Overtime Reject Tier'

    def submit(self):
        context = self._context
        record_ids = context.get('active_ids', [])
        for rec in record_ids:
            overtime_id = self.env['hr.overtime'].search([('id', '=', rec),('state', 'in', ['draft'])])
            if overtime_id:
                overtime_id.reject_tier()
