from odoo import models, api, fields


class PayslipOverTime(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def get_inputs(self, contracts, date_from, date_to):
        """
        function used for writing overtime record in payslip
        input tree.

        """
        # res, overtime_ids = super(PayslipOverTime, self).get_inputs(contracts, date_from, date_to)
        res = super(PayslipOverTime, self).get_inputs(contracts, date_from, date_to)

        # # contract = self.contract_id
        # # overtime_type_id = self.env.ref('ohrms_overtime.hr_salary_rule_overtime')
        # overtime_transport_id = self.env.ref('overtime_dev.hr_salary_rule_overtime_transport')
        # overtime_meal_id = self.env.ref('overtime_dev.hr_salary_rule_overtime_meal')
        #
        # # overtime = self.env['hr.overtime'].read_group(
        # #     domain=[('employee_id', '=', self.employee_id.id),
        # #             ('contract_id', '=', self.contract_id.id),
        # #             ('state', '=', 'approved'),
        # #             ('payslip_paid', '=', False)],
        # #     fields=["cash_hrs_amount"],
        # #     groupby=[],
        # # )
        # # for data in overtime:
        # #     overtime_amt = data['cash_hrs_amount']
        # contract_id = contracts[0] or self.contract_id
        # employee_id = contract_id.employee_id or self.employee_id
        #
        # overtime_trn = self.env['hr.overtime'].search_count([
        #     ('employee_id', '=', employee_id.id),
        #     ('contract_id', '=', contract_id.id),
        #     ('transport_allowance', '=', True),
        #     ('state', '=', 'approved'),
        #     ('payslip_paid', '=', False)
        # ])
        # overtime_meal = self.env['hr.overtime'].search_count([
        #     ('employee_id', '=', employee_id.id),
        #     ('contract_id', '=', contract_id.id),
        #     ('meal_allowance', '=', True),
        #     ('state', '=', 'approved'),
        #     ('payslip_paid', '=', False)
        # ])
        #
        # # if overtime_amt:
        # #     input_data_type = {
        # #         'name': overtime_type_id.name,
        # #         'code': overtime_type_id.code,
        # #         'amount': overtime_amt,
        # #         'contract_id': contract.id,
        # #     }
        # #     res.append(input_data_type)
        # if overtime_trn:
        #     div_transport = int(self.env['ir.config_parameter'].sudo().get_param('transport_division_month'))  # , "1")
        #     if div_transport <= 0:
        #         div_transport = 1
        #     cash_transport = contract_id.tunjangan_transport / div_transport
        #     input_data_transport = {
        #         'name': overtime_transport_id.name,
        #         'code': overtime_transport_id.code,
        #         'amount': cash_transport * overtime_trn,
        #         'contract_id': contract_id.id,
        #     }
        #     res.append(input_data_transport)
        # if overtime_meal:
        #     cash_meal = float(contract_id.tunjangan_makan)
        #     input_data_meal = {
        #         'name': overtime_meal_id.name,
        #         'code': overtime_meal_id.code,
        #         'amount': cash_meal * overtime_meal,
        #         'contract_id': contract_id.id,
        #     }
        #     res.append(input_data_meal)
        return res #, overtime_ids

    def action_payslip_cancel(self):
        for recd in self.overtime_ids:
            if recd.type == 'cash':
                recd.payslip_paid = False
        return super(PayslipOverTime, self).action_payslip_cancel()

    @api.model_create_multi
    def create(self, vals):
        res = super(PayslipOverTime, self).create(vals)
        if 'overtime_ids' in vals and vals['overtime_ids'][0][2]:
            for overtime_id in vals['overtime_ids'][0][2]:
                self.env['hr.overtime'].sudo().browse(overtime_id).update({
                    'payslip_period': res.date_to,
                })
        return res

    def write(self, vals):
        if 'overtime_ids' in vals and vals['overtime_ids'][0][2]:
            for overtime_id in vals['overtime_ids'][0][2]:
                self.env['hr.overtime'].sudo().browse(overtime_id).update({
                    'payslip_period': self.date_to,
                })
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
