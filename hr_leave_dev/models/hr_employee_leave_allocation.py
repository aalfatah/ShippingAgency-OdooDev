from odoo import api, fields, models, _
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta


class HolidaysAllocation(models.Model):
    _name = "hr.employee.leave.allocation"
    _rec_name = "employee_id"
    _description = "Leave Allocation Next Date"

    # def first_contract_date(self):
    #     return date.today()

    employee_id = fields.Many2one('hr.employee', string="Employee")
    leave_type_id = fields.Many2one('hr.leave.type', string="Leave Type", domain=[('validity_by','=','allocation')]) 
    next_allocation_date = fields.Date(string="Next Allocation Date") # ,default=first_contract_date)

    def sch_employee_leave(self):
        leave_type_ids = self.env['hr.leave.type'].sudo().search([('validity_by', '=', 'allocation')])
        for leave_type_id in leave_type_ids:
            if leave_type_id.repeated_frequency:
                emps = self.env['hr.employee'].sudo().search([('active', '=', True)])
                for emp in emps:
                    if emp.first_contract_date and int((date.today().year - emp.first_contract_date.year) / leave_type_id.repeated_frequency) >= 1:
                        start_date = date(date.today().year, emp.first_contract_date.month, emp.first_contract_date.day)
                        if start_date == date.today():
                            # start_date = date(date.today().year - 1, emp.first_contract_date.month, emp.first_contract_date.day)
                            if int((start_date.year - emp.first_contract_date.year) / leave_type_id.repeated_frequency) >= 1:
                                # end_date = start_date + relativedelta(years=leave_type_id.repeated_frequency, days=-1)
                                end_date = start_date + relativedelta(months=leave_type_id.validity_interval, days=-1)
                                vals = {
                                    'date_from':  start_date,
                                    'date_to':  end_date,
                                    'name': 'Auto Generated - Leave Quota',
                                    'state': 'draft',
                                    'employee_id': emp.id,
                                    'holiday_type': 'employee',
                                    'holiday_status_id': leave_type_id.id,
                                    'number_of_days': leave_type_id.leave_quota,
                                }
                                self.env['hr.leave.allocation'].create(vals)
            # else:
            #     for emp in self.search([('next_allocation_date', '=', date.today())]):
            #         vals = {
            #             'date_from' :  date.today(),
            #             'date_to' :  emp.next_allocation_date,
            #             'name'  : 'Auto Generated - Leave Quota',
            #             'state' : 'draft',
            #             'employee_id' : emp.employee_id.id,
            #             'holiday_type' : 'employee',
            #             'holiday_status_id' : leave_type_id.id,
            #             'number_of_days_display' : leave_type_id.leave_quota,
            #         }
            #         self.env['hr.leave.allocation'].create(vals)

