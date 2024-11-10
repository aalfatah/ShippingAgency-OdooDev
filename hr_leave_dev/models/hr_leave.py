from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_compare
import datetime


class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    @api.constrains('state', 'number_of_days', 'holiday_status_id')
    def _check_holidays(self):
        if self.holiday_status_id.validity_by == 'allocation':
            # curr = self.date_from
            # while curr <= self.date_to:
            #     workday = self._get_number_of_days(curr, self.date_to - datetime.timedelta((self.date_to - curr).days), self.employee_id.id)['days']
            #     curr += datetime.timedelta(1)
            mapped_days = self.get_employees_days_allocation(self.mapped('employee_id').ids)
            for holiday in self:
                if holiday.holiday_type != 'employee' or not holiday.employee_id or holiday.holiday_status_id.allocation_type == 'no':
                    continue
                leave_days = mapped_days[holiday.employee_id.id][holiday.holiday_status_id.id]
                if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
                    raise ValidationError(_('The number of remaining time off is not sufficient for this time off type.\n'
                                            'Please also check the time off waiting for validation.'))
        else:
            super(HolidaysRequest, self)._check_holidays()

    def get_employees_days_allocation(self, employee_ids):
        result = {
            employee_id: {
                leave_type.id: {
                    'max_leaves': 0,
                    'leaves_taken': 0,
                    'remaining_leaves': 0,
                    'virtual_remaining_leaves': 0,
                    'virtual_leaves_taken': 0,
                } for leave_type in self.mapped('holiday_status_id')
            } for employee_id in employee_ids
        }

        allocations = self.env['hr.leave.allocation'].search([
            ('employee_id', 'in', employee_ids),
            ('state', 'in', ['confirm', 'validate1', 'validate']),
            ('holiday_status_id', 'in', self.mapped('holiday_status_id').ids),
            # ('date_from', '<=', self.date_from),
            # ('date_to', '>=', self.date_to),
        ], order="date_from asc")
        request_ids = []
        if self.id:
            request_ids.append(self.id)
        for allocation in allocations.sudo():
            status_dict = result[allocation.employee_id.id][allocation.holiday_status_id.id]
            if allocation.state == 'validate':
                # note: add only validated allocation even for the virtual
                # count; otherwise pending then refused allocation allow
                # the employee to create more leaves than possible
                status_dict['virtual_remaining_leaves'] += (allocation.number_of_hours_display
                                                            if allocation.type_request_unit == 'hour'
                                                            else allocation.number_of_days)
                status_dict['max_leaves'] += (allocation.number_of_hours_display
                                              if allocation.type_request_unit == 'hour'
                                              else allocation.number_of_days)
                status_dict['remaining_leaves'] += (allocation.number_of_hours_display
                                                    if allocation.type_request_unit == 'hour'
                                                    else allocation.number_of_days)

            requests = self.env['hr.leave'].search([
                ('employee_id', 'in', employee_ids),
                ('state', 'in', ['confirm', 'validate1', 'validate']),
                ('holiday_status_id', 'in', self.mapped('holiday_status_id').ids),
                ('date_from', '>=', allocation.date_from),
                ('date_to', '<=', allocation.date_to),
                ('id', 'not in', request_ids)
            ], order="date_from asc")
            # request_ids += requests.ids
            if requests:
                for request in requests:
                    if status_dict['remaining_leaves'] > 0:
                        status_dict = result[request.employee_id.id][request.holiday_status_id.id]
                        status_dict['virtual_remaining_leaves'] -= (request.number_of_hours_display
                                                                    if request.leave_type_request_unit == 'hour'
                                                                    else request.number_of_days)
                        status_dict['virtual_leaves_taken'] += (request.number_of_hours_display
                                                                if request.leave_type_request_unit == 'hour'
                                                                else request.number_of_days)
                        if request.state == 'validate':
                            status_dict['leaves_taken'] += (request.number_of_hours_display
                                                            if request.leave_type_request_unit == 'hour'
                                                            else request.number_of_days)
                            status_dict['remaining_leaves'] -= (request.number_of_hours_display
                                                                if request.leave_type_request_unit == 'hour'
                                                                else request.number_of_days)
                        request_ids.append(request.id)
                    else:
                        status_dict['max_leaves'] = 0
                        status_dict['leaves_taken'] = 0
                        status_dict['remaining_leaves'] = 0
                        status_dict['virtual_remaining_leaves'] = 0
                        status_dict['virtual_leaves_taken'] = 0

        status_dict = result[self.employee_id.id][self.holiday_status_id.id]
        status_dict['virtual_remaining_leaves'] -= (self.number_of_hours_display
                                                    if self.leave_type_request_unit == 'hour'
                                                    else self.number_of_days)
        status_dict['virtual_leaves_taken'] += (self.number_of_hours_display
                                                if self.leave_type_request_unit == 'hour'
                                                else self.number_of_days)
        if self.state == 'validate':
            status_dict['leaves_taken'] += (self.number_of_hours_display
                                            if self.leave_type_request_unit == 'hour'
                                            else self.number_of_days)
            status_dict['remaining_leaves'] -= (self.number_of_hours_display
                                                if self.leave_type_request_unit == 'hour'
                                                else self.number_of_days)

        return result
