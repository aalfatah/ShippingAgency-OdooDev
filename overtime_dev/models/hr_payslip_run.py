# -*- coding: utf-8 -*-
""" HR Payroll Batch Journal Entry """

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    def close_payslip_run(self):
        super(HrPayslipRun, self).close_payslip_run()

        for recd in self.slip_ids.overtime_ids:
            if recd.type == 'cash':
                recd.payslip_paid = True

    def draft_payslip_run(self):
        for recd in self.slip_ids.overtime_ids:
            if recd.type == 'cash':
                recd.payslip_paid = False

        return super(HrPayslipRun, self).draft_payslip_run()
