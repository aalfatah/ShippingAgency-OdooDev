# -*- coding: utf-8 -*-

from dateutil import relativedelta
from datetime import datetime
from datetime import timedelta
from pytz import timezone
import pandas as pd
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HrOverTime(models.Model):
    _inherit = 'hr.overtime'
    _rec_name = "employee_name"

    def _get_leave_ids(self):
        for overtime in self:
            domain = []
            if overtime.date_from:
                date_from = overtime.date_from.replace(day=1) - timedelta(days=30)
                date_to = overtime.date_to.replace(day=1) + timedelta(days=100)
                domain.append(('date_from', '>=', date_from))
                domain.append(('date_to', '<=', date_to))
                if overtime.employee_id:
                    domain.append(('|'))
                domain.append(('resource_id', '=', False))
                if overtime.employee_id:
                    domain.append(('resource_id', '=', overtime.employee_id.resource_id.id))
            overtime.global_leaves = self.env['resource.calendar.leaves'].sudo().search(domain)

    day_type = fields.Selection(
        selection=[
            ("working_day", "Working Day"),
            ("day_off", "Day Off"),
            ("public_holiday", "Public Holiday"),
            ("special_holiday", "Special Holiday"),
        ],
        string="Day Type",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
        readonly=True,
    )
    type = fields.Selection([('cash', 'Cash'), ('leave', 'leave')], default="cash", required=True, string="Type")
    overtime_type_id = fields.Many2one('overtime.type', tracking=True)
    rate_hours = fields.Float(string="TUL", tracking=True)
    days_no = fields.Float('No. of Days')
    payslip_period = fields.Date(string='Period', readonly=True)
    employee_name = fields.Char(related="employee_id.name")
    color = fields.Integer(string="color", compute="get_color" ,store=True, readonly=False, default=1)
    # work_shift_ids = fields.One2many(related='employee_id.contract_id.shift_schedule')
    contract_id = fields.Many2one('hr.contract', string="Contract", domain="[('employee_id', '=', employee_id), ('state', 'in', ['open','close'])]", readonly=False)
    global_leaves = fields.One2many('resource.calendar.leaves', compute=_get_leave_ids, related='')
    # shift_ids = fields.One2many(related='employee_id.shift_ids')
    # work_day = fields.Boolean(string="Working Day")
    cash_hrs_amount = fields.Float(string='Overtime Hours Amount', readonly=True) #, groups='hr_payroll_community.group_hr_payroll_community_user,hr_payroll_community.group_hr_payroll_community_manager')
    cash_day_amount = fields.Float(string='Overtime Days Amount', readonly=True) #, groups='hr_payroll_community.group_hr_payroll_community_user,hr_payroll_community.group_hr_payroll_community_manager')

    duration_type = fields.Selection(selection='_get_duration_type', string="Duration Type", default="hours", required=True)
    days_no_tmp_period = fields.Float('Hours / Period')

    @api.model
    def _get_duration_type(self):
        return [('hours', 'Hour'), ('days', 'Day'), ('period', 'Period')]

    # @api.model_create_multi
    @api.model
    def create(self, values):
        if 'contract_id' not in values:
            values['contract_id'] = self.env['hr.employee'].browse(values['employee_id']).contract_id.id
        val = super(HrOverTime, self).create(values)
        return val

    @api.depends('state')
    def get_color(self):
        for line in self:
            if line.state == 'draft':
                line.color = 1
            if line.state == 'f_approve':
                line.color = 3
            if line.state == 'approved':
                line.color = 13
            if line.state == 'refused':
                line.color = 28

    @api.depends('date_from', 'date_to', 'contract_id')
    def _get_days(self):
        for recd in self:
            if recd.date_from and recd.date_to:
                if recd.date_from > recd.date_to:
                    raise ValidationError('Start Date must be less than End Date')
        for sheet in self.filtered(lambda o: o.state == 'draft'):
            if sheet.date_from and sheet.date_to:
                break_hour = 0
                break_hour_from = self.env['ir.config_parameter'].sudo().get_param('break_hour_from', 0)
                break_hour_to = self.env['ir.config_parameter'].sudo().get_param('break_hour_to', 0)
                if break_hour_from:
                    break_hour_from = break_hour_from.replace('.',':')
                    break_hour_from = datetime.strptime(break_hour_from, "%H:%M")
                if break_hour_to :
                    break_hour_to = break_hour_to.replace('.',':')
                    break_hour_to = datetime.strptime(break_hour_to, "%H:%M")

                if break_hour_from and break_hour_to :
                    break_hour = relativedelta.relativedelta(break_hour_to, break_hour_from).hours

                timezone = self._context.get('tz') or self.env.user.partner_id.tz or 'UTC'
                self_tz = self.with_context(tz=timezone)
                start_dt = fields.Datetime.context_timestamp(self_tz, fields.Datetime.from_string(sheet.date_from))
                finish_dt = fields.Datetime.context_timestamp(self_tz, fields.Datetime.from_string(sheet.date_to))
                s = finish_dt - start_dt
                difference = relativedelta.relativedelta(finish_dt, start_dt)
                hours = difference.hours

                start_tm = datetime.strftime(start_dt, '%H:%M')
                start_tm = datetime.strptime(start_tm, "%H:%M")
                finish_tm = datetime.strftime(finish_dt, '%H:%M')
                finish_tm = datetime.strptime(finish_tm, "%H:%M")

                if start_tm < break_hour_from and finish_tm > break_hour_to:
                    hours = hours - break_hour

                minutes = difference.minutes
                days_in_mins = s.days * 24 * 60
                hours_in_mins = hours * 60
                days_no = ((days_in_mins + hours_in_mins + minutes) / (24 * 60))

                diff = sheet.date_to - sheet.date_from
                days, seconds = diff.days, diff.seconds
                hours = days * 24 + seconds / 3600

                if start_tm < break_hour_from and finish_tm > break_hour_to:
                    hours = hours - break_hour

                sheet.update({
                    'days_no_tmp': hours if sheet.duration_type == 'hours' else (days_no if sheet.duration_type == 'days' else sheet.days_no_tmp_period),
                })
    
    def _get_rate_hours(self):
        for row in self:
            rate = 0.00
            hours = row.days_no_tmp
            for line in row.overtime_type_id.rule_line_ids.filtered(lambda l: l.from_hrs <= hours):
                if line.to_hrs <= hours:
                    rate += line.hrs_amount * (line.to_hrs - (0 if rate == 0 else line.from_hrs))
                else:
                    rate += line.hrs_amount * (hours - (0 if rate == 0 else line.from_hrs))

            row.rate_hours = rate
            # row.rate_hours = round(rate, 2)
            # row.rate_hours = int(rate * 100) / 100

    def cancel(self):
        for row in self:
            if row.payslip_period:
                raise UserError('You cannot cancel the overtimes due to have been processed in payslip.')
            else:
                row.rate_hours = 0
                if row.state == 'approved':
                    row.cash_hrs_amount = 0
                row.overtime_type_id = False
                row.state = 'draft'

    @api.onchange('rate_hours')
    def _onchange_rate_hours(self):
        if self.state == 'f_approve':
            cash_amount = 0
            if self.overtime_type_id.rule_line_ids and self.duration_type in ('hours','period'):
                if self.contract_id.over_hour:
                    # cash_amount = round(self.contract_id.over_hour * self.rate_hours, -2)
                    cash_amount = self.contract_id.over_hour * self.rate_hours
                else:
                    raise UserError(_("Hour Overtime Needs Hour Wage in Employee Contract."))

            self.write({
                'cash_hrs_amount': cash_amount,
            })

    def approve(self):
        self._onchange_rate_hours()
        return super(HrOverTime, self).approve()

    @api.onchange('date_from', 'date_to', 'employee_id', 'overtime_type_id', 'state')
    def _onchange_date(self):
        if self.employee_id:
            if self.date_from:
                contract_id = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id),
                                                              ('state', 'in', ['open', 'close']),
                                                              ('date_start', '<=', self.date_from)], order='date_start desc',
                                                             limit=1)
                self.contract_id = contract_id.id
            else:
                self.contract_id = self.employee_id.contract_id.id
        holiday = False
        holiday_str = ' '
        day_type = 'working_day'
        day_off_name = ''
        if self.contract_id and self.date_from and self.date_to:
            if self.state == 'draft' or not self.overtime_type_id: # self.orvertime_type_id != self._origin.orvertime_type_id:
                global_leave = self.env['resource.calendar.leaves'].search([('resource_id','=',False),
                                                                            ('calendar_id','=',False),
                                                                            # ('date_from','<=',self.date_from.replace(tzinfo=timezone('UTC')).astimezone(timezone(self.employee_id.tz))),
                                                                            ('date_from','<=',self.date_from),
                                                                            # ('date_to','>=',self.date_to.replace(tzinfo=timezone('UTC')).astimezone(timezone(self.employee_id.tz)))
                                                                            ('date_to','>=',self.date_from)
                                                                            ])
                # for leaves in self.contract_id.resource_calendar_id.global_leave_ids:
                for leaves in global_leave:
                    leave_dates = pd.date_range(leaves.date_from, leaves.date_to, freq='s')
                    overtime_dates = pd.date_range(self.date_from.replace(tzinfo=timezone('UTC')).astimezone(timezone(self.employee_id.tz)),
                                                   self.date_to.replace(tzinfo=timezone('UTC')).astimezone(timezone(self.employee_id.tz)))
                    for over_time in overtime_dates:
                        if over_time in leave_dates:
                            holiday = True
                            religion = self.employee_id.religion if self.employee_id.religion != 'katholik' else 'kristen'
                            if religion == leaves.religion:
                                day_type = leaves.holiday_type
                                holiday_type = 'Special Holiday'
                            else:
                                day_type = 'public_holiday'
                                holiday_type = 'Public Holiday'
                            day_off_name = leaves.name
                            # holiday_str = 'You have %s , %s in your Overtime request.' % (holiday_type, leaves.name)
                            break
                if not holiday:
                    overtime_dates = pd.date_range(self.date_from.replace(tzinfo=timezone('UTC')).astimezone(timezone(self.employee_id.tz)),
                                                   self.date_to.replace(tzinfo=timezone('UTC')).astimezone(timezone(self.employee_id.tz)))
                    day_type = "day_off"
                    holiday_type = 'Day Off'
                    for over_time in overtime_dates:
                        for work_schedule in self.employee_id.resource_calendar_id.attendance_ids:
                            if int(work_schedule.dayofweek) == over_time.dayofweek:
                                day_type = 'working_day'
                                break
                overtime_type = self.env['overtime.type'].search([('day_type','=',day_type)],limit=1).id
            else:
                overtime_type = self.overtime_type_id.id
            cash_amount = 0
            if self.state == 'f_approve':
                self.overtime_type_id = overtime_type
                self._get_rate_hours()
                if self.overtime_type_id.rule_line_ids and self.duration_type in ('hours','period'):
                    if self.contract_id.over_hour:
                        # cash_amount = round(self.contract_id.over_hour * self.rate_hours, -2)
                        cash_amount = self.contract_id.over_hour * self.rate_hours
                    else:
                        raise UserError(_("Hour Overtime Needs Hour Wage in Employee Contract."))
                elif self.overtime_type_id.rule_line_ids and self.duration_type == 'days':
                    for recd in self.overtime_type_id.rule_line_ids:
                        if recd.from_hrs < self.days_no_tmp <= recd.to_hrs and self.contract_id:
                            if self.contract_id.over_day:
                                cash_amount = self.contract_id.over_day * recd.hrs_amount
                                # self.cash_day_amount = cash_amount
                            else:
                                raise UserError(_("Day Overtime Needs Day Wage in Employee Contract."))

            if day_type != 'working_day':
                holiday_str = 'You have %s, %s in your Overtime request.' % (holiday_type, day_off_name)

            self.write({
                'day_type': day_type,
                'public_holiday': holiday_str,
                'overtime_type_id': overtime_type,
                'cash_hrs_amount': cash_amount,
            })

            if self.employee_id.resource_calendar_id:
                calendar = self.employee_id.resource_calendar_id
                tz = timezone(calendar.tz)
                date_from = datetime.combine(self.date_from.date(), datetime.min.time()).replace(tzinfo=tz)
                date_to = datetime.combine(self.date_to.date(), datetime.max.time()).replace(tzinfo=tz)
                hr_attendance = self.env['hr.attendance'].search(
                    [('check_in', '>=', date_from),
                     ('check_out', '<=', date_to),
                     ('employee_id', '=', self.employee_id.id)])
                self.update({
                    'attendance_ids': [(6, 0, hr_attendance.ids)]
                })

    def submit_to_f(self):
        val = super(HrOverTime, self).submit_to_f()
        self._onchange_date()
        return val


class HrOverTimeType(models.Model):
    _inherit = 'overtime.type'

    day_type = fields.Selection(
        selection=[
            ("working_day", "Working Day"),
            ("day_off", "Day Off"),
            ("public_holiday", "Public Holiday"),
            ("special_holiday", "Special Holiday"),
        ],
        string="Day Type",
    )
    duration_type = fields.Selection(selection='_get_duration_type', string="Duration Type", default="hours", required=True)

    @api.model
    def _get_duration_type(self):
        return [('hours', 'Hour'), ('days', 'Day'), ('period', 'Period')]


class HrOverTimeTypeRule(models.Model):
    _inherit = 'overtime.type.rule'
