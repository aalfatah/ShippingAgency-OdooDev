from odoo import api, fields, models, _
# access_employee_tax_status,employee.tax.status.user,model_employee_tax_status,hr.group_hr_user,1,1,0,0
# access_employee_tax_status_manager,employee.tax.status.manager,model_employee_tax_status,hr.group_hr_manager,1,1,1,1
# access_employee_tax_status_line,employee.tax.status.line.user,model_employee_tax_status_line,hr.group_hr_user,1,1,0,0
# access_employee_tax_status_line_manager,employee.tax.status.line.manager,model_employee_tax_status_line,hr.group_hr_manager,1,1,1,1


class EmployeeTaxStatus(models.Model):
    _name = "employee.tax.status"
    _description = 'Employee Tax Status'

    name = fields.Char(string='Title')
    date = fields.Date(string='Date')
    remarks = fields.Text(string="Remark")
    state = fields.Selection([('draft', 'Draft'),('done', 'Done'),('cancel', 'Cancel')], string='State' ,default='draft')
    tax_change_count = fields.Integer(string="Employee", compute="_get_tax_change_count")
    tax_change_only = fields.Boolean()
    line_ids = fields.One2many('employee.tax.status.line','tax_status_id', string="Line")
    line_all_ids = fields.One2many('employee.tax.status.line','tax_status_id', string="Line", domain=[('updated','=',True),('tax_status_id.tax_change_only','=',True)])


    def _get_tax_change_count(self):
        for line in self:
            line.tax_change_count = len(line.line_ids.filtered(lambda t: t.tax_status != t.tax_status_prev))

    @api.onchange('tax_change_only')
    def toggle_tax_change(self):
        self.tax_change_only = not self.tax_change_only

    def action_populate(self):
        tax_line = self.env['employee.tax.status.line'].search([('tax_status_id', '=', self.id)])
        for row in tax_line:
            row.unlink()

        populate = self.env['hr.employee'].sudo().search([])
        arr_populate = []
        for line in populate :
            child = int(line.children)
            family_status = "%s/%s" % (line.marital == 'married' and 'K' or 'TK', child)
            tax_status = "%s/%s" % (line.marital == 'married' and 'K' or 'TK', min(child, 3))
            hr_tax = self.env['hr.payroll.ptkp'].search([('name', '=', tax_status)],limit=1)
            arr_populate.append([0, 0, {'employee_id': line.id, 'family_status': family_status, 'tax_status_prev': line.tax_status.id, 'tax_status': hr_tax.id}])
        self.line_ids = arr_populate

    def action_export_to_excel(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/excel_report/%s' % (self.id),
            'target': 'new',
        }

    def action_post(self):
        for line in self.line_ids.filtered(lambda t: t.tax_status != t.tax_status_prev):
            emp = self.env['hr.employee'].sudo().search([('id','=',line.employee_id.id)],limit=1)
            emp.tax_status = line.tax_status
        self.state = 'done'

    def action_cancel(self):
        for line in self.line_ids.filtered(lambda t: t.tax_status != t.tax_status_prev):
            emp = self.env['hr.employee'].sudo().search([('id','=',line.employee_id.id)],limit=1)
            emp.tax_status = line.tax_status_prev
        self.state = 'cancel'

    def action_set_to_Draft(self):
        self.state = 'draft'


class EmployeeTaxStatusLine(models.Model):
    _name = "employee.tax.status.line"
    _description = 'Employee Tax Status Line'

    tax_status_id = fields.Many2one('employee.tax.status', string="Tax Status", ondelete="cascade")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    family_status = fields.Char(string="Family Status")
    tax_status_prev = fields.Many2one('hr.payroll.ptkp', string="Last Tax Status")
    tax_status = fields.Many2one('hr.payroll.ptkp', string="New Tax Status")
    updated = fields.Boolean(string="Updated" ,default=False ,compute="toggle_update", store=True)

    @api.depends('tax_status_prev','tax_status')
    def toggle_update(self):
        for line in self:
            if line.tax_status_prev.id == line.tax_status.id:
                line.updated = False
            else:
                line.updated = True