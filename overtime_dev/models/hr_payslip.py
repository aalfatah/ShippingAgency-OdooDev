from odoo import models, api, fields


class PayslipOverTime(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def get_inputs(self, contracts, date_from, date_to):
        # res, overtime_ids = super(PayslipOverTime, self).get_inputs(contracts, date_from, date_to)
        res = super(PayslipOverTime, self).get_inputs(contracts, date_from, date_to)
        return res #, overtime_ids

    def action_payslip_cancel(self):
        for recd in self.overtime_ids:
            if recd.type == 'cash':
                recd.payslip_paid = False
        return super(PayslipOverTime, self).action_payslip_cancel()

    @api.model_create_multi
    def create(self, vals):
        res = super(PayslipOverTime, self).create(vals)
        if 'overtime_ids' in vals[0] and vals[0]['overtime_ids'][0][2]:
            for overtime_id in vals[0]['overtime_ids'][0][2]:
                self.env['hr.overtime'].sudo().browse(overtime_id).update({'payslip_period': res.date_to,})
        return res

    def write(self, vals):
        # if 'overtime_ids' in vals and vals['overtime_ids'][0][2]:
        #     for overtime_id in vals['overtime_ids'][0][2]:
        #         self.env['hr.overtime'].sudo().browse(overtime_id).update({
        #             'payslip_period': self.date_to,
        #         })
        result = super(PayslipOverTime, self).write(vals)
        return result

    def unlink(self):
        for recd in self.overtime_ids:
            if recd.type == 'cash':
                recd.payslip_period = False
        return super(PayslipOverTime, self).unlink()


class PayslipRunOverTime(models.Model):
    _inherit = 'hr.payslip.run'

    def unlink(self):
        for slip in self.slip_ids:
            slip.unlink()
        return super(PayslipRunOverTime, self).unlink()
