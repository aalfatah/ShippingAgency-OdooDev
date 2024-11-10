from odoo import api, fields, models, _

class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"


    global_leave_ids = fields.One2many(
            'resource.calendar.leaves', 'calendar_id', 'Global Time Off',
            compute='_compute_global_leave_ids', store=True, readonly=False,
            domain=[], copy=True,
        )

    @api.depends('company_id')
    def _compute_global_leave_ids(self):
        for calendar in self.filtered(lambda c: not c._origin or c._origin.company_id != c.company_id):
            calendar.write({
                'global_leave_ids': [(5, 0, 0)] + [
                    (0, 0, leave._copy_leave_vals()) for leave in calendar.company_id.resource_calendar_id.global_leave_ids]
            })

    def _copy_leave_vals(self):
        self.ensure_one()
        return {
            'name': self.name,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'time_type': self.time_type,
        }