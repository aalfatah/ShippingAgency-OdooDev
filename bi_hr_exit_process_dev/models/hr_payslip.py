from odoo import models, fields, api, _
from datetime import datetime, time
from odoo.exceptions import UserError


class HrPayslip(models.Model):
	_inherit = 'hr.payslip'

	resign_this_period = fields.Boolean('Is Resign This Period', compute='_get_exit_status',
										search='_search_resigned_payslip')
	resign_date = fields.Date('Resign Date', related='employee_id.resign_date', store=True, readonly=False)
	resign_work_days = fields.Integer('Calendar Days', compute='_calc_exit_work_days')
	pay_resign_proportional = fields.Float(string='Resign Proportional', compute='_calc_exit_work_days')

	def _search_resigned_payslip(self, operator, value):
		if operator not in ['=', '!='] or not isinstance(value, bool):
			raise UserError(_('Operation not supported'))
		if (operator == '!=' and value is False) or (operator == '=' and value is True):
			return [('resign_date', '!=', False)]
		else:
			return [('resign_date', '=', False)]

	def _get_exit_status(self):
		for payslip in self:
			if payslip.resign_date:
				# payslip.resign_this_period = payslip.resign_date >= payslip.date_from and payslip.resign_date <= payslip.date_to
				payslip.resign_this_period = payslip.resign_date <= payslip.date_to
			else:
				payslip.resign_this_period = False

	@api.depends('resign_date')
	def _calc_exit_work_days(self):
		for slip in self:
			if slip.resign_date:
				if slip.date_from <= slip.resign_date <= slip.date_to:
					day_from = datetime.combine(fields.Date.from_string(slip.date_from), time.min)
					day_to = datetime.combine(fields.Date.from_string(slip.resign_date), time.max)
					# work_days = payslip.employee_id.get_work_days_data(day_from, day_to, calendar=payslip.contract_id.resource_calendar_id)
					# payslip.resign_work_days = work_days['days']
					calendar_days = day_to - day_from
					slip.resign_work_days = calendar_days.days + 1
					days_payslip = (slip.date_to - slip.date_from).days + 1
					slip.pay_resign_proportional = slip.resign_work_days / days_payslip
				elif slip.date_to < slip.resign_date:
					day_from = datetime.combine(fields.Date.from_string(slip.date_from), time.min)
					day_to = datetime.combine(fields.Date.from_string(slip.date_to), time.max)
					# work_days = payslip.employee_id.get_work_days_data(day_from, day_to, calendar=payslip.contract_id.resource_calendar_id)
					# payslip.resign_work_days = work_days['days']
					calendar_days = day_to - day_from
					slip.resign_work_days = calendar_days.days + 1
					days_payslip = (slip.date_to - slip.date_from).days + 1
					slip.pay_resign_proportional = slip.resign_work_days / days_payslip
				else:
					slip.resign_work_days = 0
					slip.pay_resign_proportional = 0
			else:
				slip.resign_work_days = False
				slip.pay_resign_proportional = 1
