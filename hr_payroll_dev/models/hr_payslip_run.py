from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class HrPayslipRunInherit(models.Model):
    _inherit = "hr.payslip.run"

    # bpjs_kes_payment_date = fields.Date('BPJS Kesehatan Payment Date')
    # bpjs_tk_payment_date = fields.Date('BPJS Ketenagakerjaan Payment Date')
    payslip_count = fields.Integer(compute='_compute_payslip_count', string="Payslip Computation Details")
    # revenue_amount = fields.Float('Revenue Amount', default=0)
    # total_employees = fields.Integer('Jumlah Karyawan', compute='_get_employees', store=True, readonly=False)
    # productivity = fields.Float('Productivity', compute='_get_productivity', store=True, readonly=True)

    # @api.depends('slip_ids')
    # def _get_employees(self):
    #     for batch in self:
    #         batch.total_employees = len(batch.slip_ids)

    # @api.depends('revenue_amount','total_employees')
    # def _get_productivity(self):
    #     for batch in self:
    #         batch.productivity = 0 if batch.total_employees == 0 else batch.revenue_amount / batch.total_employees

    def _compute_payslip_count(self):
        for payslip in self:
            payslip.payslip_count = len(payslip.slip_ids)

    def action_export_to_excel(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/excel_payslip/%s' % (self.id),
            'target': 'new',
        }

    def _create_batch_move(self, payslips):
        def line_ids_update(new_line):
            amt = 0
            for line in line_ids:
                if line[2]['account_id'] == new_line[2]['account_id']:
                    amt = new_line[2]['debit'] - new_line[2]['credit'] + line[2]['debit'] - line[2]['credit']
                    line[2]['debit'] = amt > 0.0 and amt or 0.0
                    line[2]['credit'] = amt < 0.0 and -amt or 0.0
                    break
            if not amt:
                line_ids.append(new_line)

        self.ensure_one()
        currency = self.journal_id.currency_id or \
                   self.journal_id.company_id.currency_id
        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        date = self.batch_date or self.date_end
        name = _("Payslip Batch of %s") % self.name
        move_dict = {
            'narration': name,
            'ref': self.name,
            'journal_id': self.journal_id.id,
            'date': date,
        }
        for slip in payslips:
            # slip.write({'state': 'done'})
            slip.with_context(is_batch=True).action_payslip_done()

            # salary_group_id = slip.payslip_run_id.salary_group.id
            # if slip.payslip_run_id.salary_group.cost_center_id:
            #     cost_center_id = slip.payslip_run_id.salary_group.cost_center_id.id
            # else:
            #     cost_center_id = slip.employee_id.cost_center_id.id
            # if slip.payslip_run_id.salary_group.analytic_account_id:
            #     analytic_account_id = slip.payslip_run_id.salary_group.analytic_account_id.id
            # else:
            #     analytic_account_id = slip.employee_id.analytic_account_id.id

            for line in slip.details_by_salary_rule_category:
                amount = currency.round(self.credit_note and -line.total or line.total)
                if currency.is_zero(amount):
                    continue

                ledger_mapping = line.salary_rule_id.ledger_ids.search([('salary_rule_id', '=', line.salary_rule_id.id),
                                                                        ('salary_group_id', '=', slip.salary_group_id.id)])
                if not ledger_mapping:
                    ledger_mapping = line.salary_rule_id.ledger_ids.search([('salary_rule_id', '=', line.salary_rule_id.id)])
                if ledger_mapping:
                    debit_account_id = ledger_mapping.account_debit.id
                    credit_account_id = ledger_mapping.account_credit.id
                else:
                    # debit_account_id = line.salary_rule_id.account_debit.id
                    # credit_account_id = line.salary_rule_id.account_credit.id
                    continue

                if debit_account_id:
                    debit_line = (0, 0, {
                        'name': line.name,
                        'partner_id': line._get_partner_id(credit_account=False),
                        'account_id': debit_account_id,
                        'journal_id': self.journal_id.id,
                        'date': date,
                        'debit': amount > 0.0 and amount or 0.0,
                        'credit': amount < 0.0 and -amount or 0.0,
                        # 'tax_line_id': line.salary_rule_id.account_tax_id.id,
                    })
                    line_ids_update(debit_line)
                    # line_ids.append(debit_line)
                    debit_sum += debit_line[2]['debit'] - debit_line[2][
                        'credit']

                if credit_account_id:
                    credit_line = (0, 0, {
                        'name': line.name,
                        'partner_id': line._get_partner_id(credit_account=True),
                        'account_id': credit_account_id,
                        'journal_id': self.journal_id.id,
                        'date': date,
                        'debit': amount < 0.0 and -amount or 0.0,
                        'credit': amount > 0.0 and amount or 0.0,
                        # 'tax_line_id': line.salary_rule_id.account_tax_id.id,
                    })
                    line_ids_update(credit_line)
                    # line_ids.append(credit_line)
                    credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

        if currency.compare_amounts(credit_sum, debit_sum) == -1:
            acc_id = self.journal_id.default_account_id.id
            if not acc_id:
                raise UserError(_(
                    'The Expense Journal "%s" has not properly configured the Credit Account!') % (
                                    self.journal_id.name))
            adjust_credit = (0, 0, {
                'name': _('Adjustment Entry'),
                'partner_id': False,
                'account_id': acc_id,
                'journal_id': self.journal_id.id,
                'date': date,
                'debit': 0.0,
                'credit': currency.round(debit_sum - credit_sum),
            })
            line_ids.append(adjust_credit)
        elif currency.compare_amounts(debit_sum, credit_sum) == -1:
            acc_id = self.journal_id.default_account_id.id
            if not acc_id:
                raise UserError(_(
                    'The Expense Journal "%s" has not properly configured the Debit Account!') % (
                                    self.journal_id.name))
            adjust_debit = (0, 0, {
                'name': _('Adjustment Entry'),
                'partner_id': False,
                'account_id': acc_id,
                'journal_id': self.journal_id.id,
                'date': date,
                'debit': currency.round(credit_sum - debit_sum),
                'credit': 0.0,
            })
            line_ids.append(adjust_debit)
        move_dict['line_ids'] = line_ids
        move = self.env['account.move'].create(move_dict)
        self.write({'batch_move_id': move.id, 'batch_date': date})
        # move.action_post()

    def _set_payslip_draft(self):
        for rec in self:
            for slip in rec.slip_ids:
                slip.action_payslip_cancel()
                # if slip.state == "done":
                slip.write({'state': 'draft'})
                if slip.move_id:
                    slip.move_id.button_cancel()
                    slip.move_id.unlink()

    def menyetujui(self, title):
        for request in self:
            employee = self.env['hr.employee'].sudo().search([('user_id', '=', request.create_uid.id)]).parent_id
            if title == 'name':
                return employee.user_id.name
            elif title == 'job_title':
                return employee.job_id.name
            elif title == 'signature':
                return employee.user_id.signature

    def mengetahui(self, title):
        for request in self:
            employee = self.env['hr.employee'].sudo().search([('user_id', '=', request.create_uid.id)]).parent_id.parent_id
            if title == 'name':
                return employee.user_id.name
            elif title == 'job_title':
                return employee.job_id.name
            elif title == 'signature':
                return employee.user_id.signature

    def summary_employee_payslip(self):
        summary_payslip_title = []
        summary_payslip_amount = []
        first_employee = True
        for slip_id in self.slip_ids:
            i = 0
            for line_id in slip_id.line_ids.filtered(lambda r: r.appears_on_list):
                if first_employee:
                    summary_payslip_title.append(line_id.name)
                    summary_payslip_amount.append(line_id.total)
                else:
                    summary_payslip_amount[i] += line_id.total
                i += 1
            first_employee = False
        return [summary_payslip_title, summary_payslip_amount]

    def get_pres_dir(self, option):
        employee_id = self.env['hr.employee'].search([('job_id.name', '=', 'President Director')], limit=1)
        if option == 'name':
            return employee_id.name
        elif option == 'job_title':
            return employee_id.job_title
        elif option == 'signature':
            return employee_id.user_id.signature
