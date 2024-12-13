# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from datetime import datetime,date, timedelta, datetime
from odoo.exceptions import UserError
import pytz
from dateutil.relativedelta import relativedelta

date_format = "%Y-%m-%d"
FORMATROMAN = (
    ('M',  1000),
    ('CM', 900),
    ('D',  500),
    ('CD', 400),
    ('C',  100),
    ('XC', 90),
    ('L',  50),
    ('XL', 40),
    ('X',  10),
    ('IX', 9),
    ('V',  5),
    ('IV', 4),
    ('I',  1)
)


class exit_request(models.Model):
	_inherit = "exit.request"
	_order = "req_date desc"

	name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True,
					   default=lambda self: _('New'), related='')
	reason = fields.Text(string="Reason For Exit", required=True)
	resignation_type = fields.Selection(selection='_get_resignations', string='Type', required=True)
	joined_date = fields.Date(string="Join Date", related='employee_id.first_contract_date')
	end_date = fields.Date(string="Join Date", related='employee_id.contract_id.date_end')
	notice_period = fields.Char(string="Notice Period")
	checklist_ids = fields.Many2many('checklist.information','rel_exit_request_id',string="Checklist")
	job_title_id = fields.Many2one('hr.job', string="Job Title", required=False, related='employee_id.job_id', store=True)
	department_id = fields.Many2one('hr.department', string="Department", related='employee_id.department_id', store=True)
	area_id = fields.Many2one('res.area', string="Area", related='employee_id.area_id', store=True)
	pending_payroll = fields.Boolean(string="Pending Payroll")
	last_payroll_date = fields.Date(string="Last Payroll Date")
	state = fields.Selection(tracking=True)

	_sql_constraints = [('exit_employee_unique', 'unique(employee_id)', "Employee already exist!")]

	def action_done(self):
		if self.last_date:
			if self.last_date <= date.today() and not self.pending_payroll:
				self.employee_id.active = False
				self.employee_id.user_id.active = False
				# self.employee_id.address_home_id.active = False
				# self.employee_id.bank_account_id.acc_number = str(self.employee_id.bank_account_id.acc_number)+'X'
				# self.employee_id.identification_id = str(self.employee_id.identification_id) + 'X'
				contract_state = self.env['hr.contract'].sudo().search([('employee_id','=',self.employee_id.id),('state','=','open')],limit=1)
				contract_state.write({'state': 'cancel'})
		if self.pending_payroll:
			if self.last_payroll_date <= date.today():
				self.employee_id.active = False
				self.employee_id.user_id.active = False
				# self.employee_id.address_home_id.active = False
				# self.employee_id.bank_account_id.acc_number = str(self.employee_id.bank_account_id.acc_number)+'X'
				# self.employee_id.identification_id = str(self.employee_id.identification_id) + 'X'
				contract_state = self.env['hr.contract'].sudo().search([('employee_id','=',self.employee_id.id),('state','=','open')],limit=1)
				contract_state.write({'state': 'cancel'})
		self.employee_id.resign_date = self.last_date
		self.write({'state': 'done'})
		return

	def action_cancel(self):
		if self.state == 'done':
			if not self.employee_id.active:
				self.employee_id.active = True
				self.employee_id.user_id.active = True
				# self.employee_id.address_home_id.active = True
				# acc = self.employee_id.bank_account_id.acc_number
				# self.employee_id.bank_account_id.acc_number = acc.replace('X', '')
				# ident = self.employee_id.identification_id
				# self.employee_id.identification_id = ident.replace('X', '')
				contract_state = self.env['hr.contract'].sudo().search([('employee_id','=',self.employee_id.id),('state','=','cancel')],limit=1)
				contract_state.write({'state': 'open'})
		self.state = 'draft'

	def sch_req_process(self):
		# timezone = self._context.get('tz') or self.env.user.tz
		# today = datetime.now(pytz.timezone(timezone))
		# today = datetime.strptime(today.strftime("%Y-%m-%d"), '%Y-%m-%d')
		for request in self.search([('last_date', '<=', date.today()), ('state', '=', 'done'), ('pending_payroll', '=', False), ('employee_id.active', '=', True)]):
			if request.employee_id.active:
				request.employee_id.active = False
				request.employee_id.resign_date = request.last_date
				request.employee_id.user_id.active = False
				# request.employee_id.address_home_id.active = False
				# request.employee_id.bank_account_id.acc_number = str(request.employee_id.bank_account_id.acc_number)+'X'
				# request.employee_id.identification_id = str(request.employee_id.identification_id) + 'X'
				contract_state = self.env['hr.contract'].sudo().search([('employee_id','=',request.employee_id.id),('state','=','open')],limit=1)
				contract_state.write({'state': 'cancel'})
		for request in self.search([('last_payroll_date', '<=', date.today()), ('state', '=', 'done'), ('pending_payroll', '=', True), ('employee_id.active', '=', True)]):
			if request.employee_id.active:
				request.employee_id.active = False
				request.employee_id.resign_date = request.last_date
				request.employee_id.user_id.active = False
				# request.employee_id.address_home_id.active = False
				# request.employee_id.bank_account_id.acc_number = str(request.employee_id.bank_account_id.acc_number)+'X'
				# request.employee_id.identification_id = str(request.employee_id.identification_id) + 'X'
				contract_state = self.env['hr.contract'].sudo().search([('employee_id','=',request.employee_id.id),('state','=','open')],limit=1)
				contract_state.write({'state': 'cancel'})
		return

	@api.onchange('employee_id')
	def onchange_employee(self):
		self.department_id = self.employee_id.department_id.id
		self.job_title_id = self.employee_id.job_id.id
		self.partner_id = self.employee_id.address_home_id.id
		self.email = self.employee_id.work_email
		self.phone = self.employee_id.work_phone
		self.user_id = self.env.uid

		domain = {}
		domain['checklist_ids'] =  [('state','=','approved'),('employee_id.id','=',self.employee_id.id)]
		return {'domain': domain}

	@api.model
	def _get_resignations(self):
		RESIGNATION_TYPE = [
			('HABIS KONTRAK', 'HABIS KONTRAK'),
			('PENSIUN', 'PENSIUN'),
			('PHK', 'PHK'),
			('PHK MENINGGAL', 'PHK MENINGGAL'),
			('PHK SAKIT', 'PHK SAKIT'),
			('PHK EFISIENSI', 'PHK EFISIENSI'),
			('PHK KRIMINAL', 'PHK KRIMINAL'),
			('RESIGN', 'RESIGN'),
			('SELESAI MAGANG', 'SELESAI MAGANG'),
		]

		return RESIGNATION_TYPE

	def convert_to_roman(self, n):
		result = ""
		for numeral, integer in FORMATROMAN:
			while n >= integer:
				result += numeral
				n -= integer
		return result

	# @api.model_create_multi
	@api.model
	def create(self, vals):
		last_date = vals['last_date']
		tanggal = datetime.strptime(last_date, '%Y-%m-%d')
		year = tanggal.strftime("%Y")
		month = tanggal.strftime("%m")
		rom_month = self.convert_to_roman(int(month))

		if vals.get('name', _('New')) == _('New'):
			seq = self.env['ir.sequence'].next_by_code('exit.number.seq') or _('New')
			if vals['resignation_type'] and vals['last_date']:
				sequence = seq.replace('format', vals['resignation_type'] + '/' + rom_month + '/' + year)
			else:
				sequence = seq.replace('/format', '')

			vals['name'] = sequence
		res = super(exit_request, self).create(vals)

		return res

	def write(self, vals):
		if vals.get('last_date'):
			last_date = vals.get('last_date')
			tanggal = datetime.strptime(last_date, '%Y-%m-%d')
		else:
			last_date = self.last_date
			tanggal = last_date

		year = tanggal.strftime("%Y")
		month = tanggal.strftime("%m")
		rom_month = self.convert_to_roman(int(month))
		seq = str(self.name)
		seq = seq[:9]

		if vals.get('resignation_type'):
			resignation_type = vals.get('resignation_type')
		else:
			resignation_type = self.resignation_type

		if resignation_type and last_date:
			sequence = seq + resignation_type + '/' + rom_month + '/' + year
		else:
			sequence = seq

		vals['name'] = sequence

		res = super(exit_request, self).write(vals)

		return res

	def unlink(self):
		for resign in self:
			if resign.state not in ('draft', 'cancel'):
				raise UserError(_('You can not delete a termination. You must first cancel it.'))
		return super(exit_request, self).unlink()


class exit_checklist(models.Model):
	_inherit = "checklist.information"

	checklist_line_ids = fields.One2many('checklist.information.line', 'checklist_info_id', string="Checklist Line")
	# employee_id = fields.Many2one('hr.employee', related="exit_request_id.employee_id")
	employee_id = fields.Many2one('hr.employee')

	# @api.model
	# def create(self, values):
	# 	values['state'] = 'approved'
	# 	res = super(exit_checklist, self).create(values)
	# 	return res

	@api.onchange('checklist_id')
	def onchange_checklist_id(self):
		arr_checklist = []
		for line in self.checklist_id.checklist_line_ids :
			arr_checklist.append([0, 0, {'name': line.name, 'checklist_id': line.checklist_id, 'checklist_info_id': line.id}])
		
		self.responsible_user_id = self.checklist_id.responsible_user_id.id
		self.remarks = self.checklist_id.notes
		self.checklist_line_ids = arr_checklist
		return

	def unlink(self):
		for resign in self:
			if resign.state not in ('new',):
				raise UserError(_('You can not delete a termination. You must first cancel it or state is new.'))
		return super(exit_checklist, self).unlink()

	def action_cancel(self):
		self.state = 'new'


class exit_checklist_lines(models.Model):
	_name = "checklist.information.line"
	_description = 'Checklist Information Line'

	name = fields.Char(string="Name")
	checklist_id = fields.Many2one('exit.checklist')
	checklist_info_id = fields.Many2one('checklist.information', ondelete='cascade')
	done = fields.Boolean(string="Done")
