from odoo import api, fields, models, tools, _
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
import locale 
from num2words import num2words


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    payslip_run_id = fields.Many2one('hr.payslip.run', string='Payslip Batches', readonly=True, ondelete="cascade",
                                     copy=False, states={'draft': [('readonly', False)]})
    first_contract_date = fields.Date(string='First Contract Date', related='employee_id.first_contract_date')
    pay_proportional = fields.Float(string='Proportional', compute='_get_masa')
    rapel_proportional = fields.Float(string='Rapel Proportional', compute='_get_masa')
    thr_proportional = fields.Float(string='THR Proportional', compute='_get_masa')
    upk_proportional = fields.Float(string='UPK Proportional', compute='_get_masa')
    masa_start = fields.Integer(compute='_get_masa')
    masa = fields.Integer(compute='_get_masa')
    masa_year = fields.Integer(compute='_get_masa')
    masa_ytd = fields.Integer(compute='_get_masa')
    ptkp_id = fields.Many2one('hr.payroll.ptkp', string='PTKP')
    npwp = fields.Char(string='NPWP')
    bpjsks_status = fields.Boolean(string='BPJS Kesehatan')
    bpjstk_status = fields.Boolean(string='BPJS Ketenagakerjaan')
    unit_kerja = fields.Selection([('administrasi','Administrasi'), ('pabrikasi','Pabrikasi'), ('tambang','Tambang')],  string="Unit Kerja")
    # pensiun = fields.Boolean(string='Pensiun', related='employee_id.pensiun_status')
    tahun = fields.Integer(string='Tahun', compute='set_tahun', store=True)
    terbilang = fields.Char(string="Terbilang", compute="_get_terbilang")
    closing_period = fields.Boolean('Is Closing Period', compute='_get_closing_status')
    bank_id = fields.Many2one('res.bank', string='Bank') # , related='employee_id.bank_account_id.bank_id', store=True)
    gross_amt = fields.Float('Gross', compute='_get_gross_amount', store=True)
    # salary_group_id = fields.Many2one('hr.salary.group', string='Salary Group')
    payslip_input_count = fields.Integer(compute='_compute_payslip_input_count', string="Payslip Input Details")

    def _compute_payslip_input_count(self):
        for payslip in self:
            payslip.payslip_input_count = len(payslip.input_line_ids)

    @api.onchange('employee_id')
    def _onchange_employee(self):
        self.update({'bank_id': self.employee_id.bank_account_id.bank_id.id,
                     'ptkp_id': self.employee_id.ptkp_id.id,
                     'bpjsks_status': self.employee_id.bpjsks_status,
                     'bpjstk_status': False if self.resign_this_period else self.employee_id.bpjstk_status,
                     'npwp': self.employee_id.npwp,
                     'unit_kerja': self.employee_id.unit_kerja,
                     # 'salary_group_id': self.employee_id.salary_group_id,
        })

    def compute_sheet(self):
        ret = super(HrPayslip,self).compute_sheet()
        self._get_gross_amount()
        return ret

    def _get_gross_amount(self):
        for payslip in self:
            payslip.gross_amt = sum(payslip.line_ids.filtered(lambda l: l.category_id.id in (1, 2, 14)).mapped('amount'))

    def _get_closing_status(self):
        for payslip in self:
            payslip.closing_period = payslip.date_to.month == 12 and payslip.date_to.day == 31

    def _get_terbilang(self):
        value = 0
        for row in self:
            for line in row.line_ids:
                if line.code == 'NET':
                    value = round(line.total)

            row.terbilang = (num2words(value, lang="id").upper() + ' RUPIAH')

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        """
        @param contract: Browse record of contracts
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        res = []
        # fill only if the contract as a working schedule linked
        for contract in contracts.filtered(lambda c: c.resource_calendar_id):
            day_from = max(datetime.combine(fields.Date.from_string(date_from), time.min),
                           datetime.combine(fields.Date.from_string(contract.date_start), time.min))
            if contract.date_end:
                day_to = min(datetime.combine(fields.Date.from_string(date_to), time.max),
                             datetime.combine(fields.Date.from_string(contract.date_end), time.min))
            else:
                day_to = datetime.combine(fields.Date.from_string(date_to), time.max)
            leaves = {}
            overtime = {}
            calendar = contract.resource_calendar_id
            tz = timezone(calendar.tz)
            holiday_leave_id = False
            sequence = 1
            # compute worked days
            work_data = contract.employee_id.get_work_days_data(day_from, day_to, calendar=contract.resource_calendar_id)
            attendances = {
                'name': _("Normal Working Days paid at 100%"),
                'sequence': sequence,
                'code': 'WORK100',
                'number_of_days': work_data['days'],
                'number_of_hours': work_data['hours'],
                'contract_id': contract.id,
            }

            day_leave_intervals = contract.employee_id.list_leaves(day_from, day_to, calendar=contract.resource_calendar_id)
            for day, hours, leave in day_leave_intervals:
                holiday = leave.holiday_id
                holiday_leave_id = holiday.holiday_status_id.id
                hr_leave = self.env['hr.leave.report'].search([('employee_id','=',contract.employee_id.id),('holiday_status_id','=',holiday.holiday_status_id.id),('state','=','validate')])
                sisa_cuti = 0.0
                for row_cuti in hr_leave:
                    sisa_cuti += row_cuti.number_of_days
                sequence += 1
                current_leave_struct = leaves.setdefault(holiday.holiday_status_id, {
                    'name': holiday.holiday_status_id.name or _('Global Leaves'),
                    'sequence': sequence,
                    'code': holiday.holiday_status_id.code or 'GLOBAL',
                    'number_of_days': 0.0,
                    'number_of_hours': 0.0,
                    'remaining_days': 0.0,
                    'contract_id': contract.id,
                })
                current_leave_struct['number_of_hours'] += hours

                work_hours = calendar.get_work_hours_count(
                    tz.localize(datetime.combine(day, time.min)),
                    tz.localize(datetime.combine(day, time.max)),
                    compute_leaves=False,
                )
                if work_hours:
                    current_leave_struct['number_of_days'] += hours / work_hours
                    current_leave_struct['remaining_days'] = sisa_cuti
            leave_type = self.env['hr.leave.type'].search([('requires_allocation', '!=', 'no')])
            worked_days_id = False
            for row_type in leave_type:
                if row_type.id != holiday_leave_id:
                    quota = sum(self.env['hr.leave.report'].search([('employee_id', '=', contract.employee_id.id),
                                                                    ('holiday_status_id', '=', row_type.id),
                                                                    ('leave_type', '=', 'allocation'),
                                                                    ('date_from', '<=', day_to),
                                                                    ('state', '=', 'validate')]).mapped(
                        'number_of_days'))
                    hr_leave = self.env['hr.leave.report'].search([('employee_id', '=', contract.employee_id.id),
                                                                   ('holiday_status_id', '=', row_type.id),
                                                                   ('leave_type', '=', 'request'),
                                                                   ('date_from', '<=', day_to),
                                                                   ('state', '=', 'validate')])
                    cuti = 0
                    for row_cuti in hr_leave:
                        if row_cuti.date_to <= day_to:
                            cuti += abs(row_cuti.number_of_days)
                        elif row_cuti.date_from <= day_to:
                            cuti += (day_to - row_cuti.date_from).days + 1
                    sisa_cuti = quota - cuti
                    if sisa_cuti or cuti:
                        sequence += 1
                        current_leave_struct = leaves.setdefault(row_type.id, {
                            'name': row_type.name or _('Global Leaves'),
                            'sequence': sequence,
                            'code': row_type.code or 'LEAVE',
                            'number_of_days': cuti,
                            'number_of_hours': 0.0,
                            'remaining_days': sisa_cuti,
                            'contract_id': contract.id,
                        })

            # compute Overtime
            hr_input = self.env['hr.overtime'].search([('employee_id', '=', contract.employee_id.id),
                                                       # ('contract_id', '=', contract.id),
                                                       ('state', '=', 'approved'),
                                                       ('payslip_paid', '=', False),
                                                       '|', ('payslip_period', '=', False), ('payslip_period', '=', date_to),
                                                       ])
            overtime_hours = 0.0
            # meal_allowance = 0
            # transport_allowance = 0

            # transport_division_month = 20
            # res_config = self.env['res.config.settings'].search([])
            # for config in res_config:
            #     transport_division_month = config.transport_division_month

            for row in hr_input:
                # overtime_hours += row.days_no_tmp
                overtime_hours += row.rate_hours
                # if row.transport_allowance:
                #     transport_allowance = transport_allowance + 1
                # if row.meal_allowance :
                #     meal_allowance = meal_allowance + 1

            if overtime_hours > 0:
                rule = self.env.ref('ohrms_overtime.hr_salary_rule_overtime')
                sequence += 1
                overtimes = overtime.setdefault(rule.id, {
                    'name': rule.name,
                    'sequence': sequence,
                    'code': rule.code,
                    'number_of_hours': overtime_hours,
                    'contract_id': contract.id,
                })
            res.append(attendances)
            res.extend(leaves.values())
            res.extend(overtime.values())
        return res

    @api.depends('date_from')
    def set_tahun(self):
        for slip in self:
            slip.tahun = slip.date_from.year

    @api.onchange('first_contract_date','tahun','date_from','date_to')
    def _get_masa(self):
        for slip in self:
            # masa_start = False
            # masa_year = False
            if slip.first_contract_date:
                if slip.tahun > slip.first_contract_date.year:
                    masa_start = 1
                    masa_year = 12
                else:
                    month = slip.first_contract_date.month
                    day = slip.first_contract_date.day
                    masa_start = month
                    masa_year = 12 - month + 1 #- (day > 21 and 1 or 0)
                slip.masa_start = masa_start
                slip.masa_year = masa_year
                slip.masa = slip.date_from.month
                slip.masa_ytd = slip.date_from.month - masa_start + 1

                if slip.first_contract_date > slip.date_from:
                    days_payslip = (slip.date_to - slip.date_from).days + 1
                    days_work = (slip.date_to - slip.first_contract_date).days + 1
                    slip.pay_proportional = days_work / days_payslip
                else:
                    slip.pay_proportional = 1

                rapel_proportional = 0
                if slip.date_from > slip.first_contract_date > (slip.date_from - relativedelta(months=1) + relativedelta(days=19)):
                    rapel_days = (slip.date_from - slip.first_contract_date).days
                    month_days = (slip.date_from - (slip.date_from - relativedelta(months=1))).days
                    rapel_proportional = rapel_days / month_days
                slip.rapel_proportional = rapel_proportional

                # thr_proportional = 0
                # for leave_day in self.env['resource.calendar.leaves'].search([('thr_day', '=', True)], order='date_from desc'):
                #     if leave_day.date_from.year == slip.date_from.year:
                #         thr_date = leave_day.date_from.date()
                #         if slip.first_contract_date > (thr_date - relativedelta(years=1)):
                #             thr_days = (thr_date - slip.first_contract_date).days + 1
                #             if thr_days > 30:
                #                 thr_proportional = thr_days / 365
                #         else:
                #             thr_proportional = 1
                #         break
                # slip.thr_proportional = thr_proportional

                # upk_proportional = 0
                # if slip.contract_id.date_end:
                #     upk_days = (slip.contract_id.date_end - slip.contract_id.date_start).days + 1
                #     upk_proportional = upk_days / 365
                # slip.upk_proportional = upk_proportional
            else:
                slip.masa_start = False
                slip.masa_year = False
                slip.masa = False
                slip.masa_ytd = False
                slip.pay_proportional = 0
                slip.rapel_proportional = 0

    def get_date_indonesia(self, date):
        tanggal = date.day
        bulan = date.strftime('%B')
        tahun = date.year
        return "%s %s %s" % (tanggal, bulan, tahun)


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    bold_on_payslip = fields.Boolean(string='Bold on Payslip', related='salary_rule_id.bold_on_payslip')
    # payslip_run_id = fields.Many2one('hr.payslip.run', string='Payslip Batches', related="slip_id.payslip_run_id")

    @api.onchange("salary_rule_id")
    def _depend_on_salary_rule(self):
        for line in self:
            line.appears_on_payslip = line.salary_rule_id.appears_on_payslip

class HrPayslipWorkedDaysRemaining(models.Model):
    _inherit = 'hr.payslip.worked_days'

    remaining_days = fields.Float(string="Remaining Days")
    quantity = fields.Integer(string="Quantity")
