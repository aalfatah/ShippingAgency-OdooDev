from odoo import api, fields, models, _
import datetime
from odoo.exceptions import Warning, UserError
from odoo.exceptions import UserError, ValidationError
from ast import literal_eval
from datetime import date, datetime, timedelta


class TravelRequest(models.Model):
    _inherit = "travel.request"
    _order = 'name desc'

    def list_emp_pemberi_tugas(self):
        arr_employee = []
        params = self.env['ir.config_parameter'].sudo()
        pemberi_tugas_ids = params.get_param('pemberi_tugas_id', default=False)
        if pemberi_tugas_ids:
            for line in literal_eval(pemberi_tugas_ids):
                arr_employee.append(line)

        domain = [('id', 'in', arr_employee)]
        return domain

    # def list_emp_approver(self):
    #     arr_employee = []
    #     params = self.env['ir.config_parameter'].sudo()
    #     mengetahui_ids = params.get_param('mengetahui_id', default=False)
    #     if mengetahui_ids:
    #         for line in literal_eval(mengetahui_ids):
    #             arr_employee.append(line)
    #
    #     domain = [('id', 'in', arr_employee)]
    #     return domain

    travel_type_id = fields.Many2one('travel.type', string="Travel Type", required=True)
    expense_sheet_id = fields.Many2one('hr.expense.sheet', string="Expense Sheet", readonly=True)
    contact_person = fields.Char(string="Contact Person")
    req_departure_date = fields.Datetime(string="Request Departure Date", required=False)
    req_return_date = fields.Datetime(string="Request Return Date", required=False)
    line_ids = fields.One2many("travel.request.line", "travel_line_id", string="Travel Request")
    partner_id = fields.Many2one("res.partner", related="employee_id.address_home_id")
    payment_type = fields.Selection(selection=[('cash', 'Cash'), ('bank', 'Bank Transfer')], string="Payment Type")
    bank_account_id = fields.Many2one('res.partner.bank', string="Bank Account",
                                      domain="[('partner_id', '=', partner_id)]")
    customer_id = fields.Many2one('res.partner')
    # support_id = fields.Many2one('res.partner.support', related='employee_id.support_id')
    area_id = fields.Many2one('res.area')
    # sub_area_id = fields.Many2one('hr.employee.area.sub', string="Sub Area", related="employee_id.sub_area_id", store=True)
    name = fields.Char(string="Name")
    # show_leave = fields.Boolean(string="Travel Type", related="travel_type_id.show_leave")
    # leave_ids = fields.One2many(related="employee_id.leave_ids", string="Leave")
    departure_date = fields.Datetime(string="Departure Date", compute="_get_departure_date", store=True)
    return_date = fields.Datetime(string="Return Date", compute="_get_departure_date", store=True)
    return_date_str = fields.Char(compute="_get_reminder_data")
    from_area = fields.Char(string="From Area", compute="_get_departure_date", store=True)
    to_area = fields.Char(string="To Area", compute="_get_departure_date", store=True)
    total_dp = fields.Float(string="Uang Muka", compute="_get_uang_muka")
    employee_id_pemberi_tugas = fields.Many2one('hr.employee', string='Pemberi Tugas', domain=list_emp_pemberi_tugas)
    # employee_id_approver = fields.Many2one('hr.employee', string='Mengetahui' , domain=list_emp_approver)
    mail_reminder = fields.Char(string="Mail Reminder", compute="_get_mail_reminder")
    cnt_reminder = fields.Integer('Reminder', readonly=True, default=0, group_operator=False)
    last_reminder = fields.Date('Last Reminder', readonly=True)
    nilai_advance = fields.Float(string="Nilai Advance", compute="_get_uang_muka")
    nilai_advance_str = fields.Char(compute="_get_reminder_data")
    reservation = fields.Selection(selection=[('company', 'Company'), ('employee', 'Employee')], string="Reservation",
                                   compute="_get_reservation", store=True)
    description = fields.Char(string="Description")

    @api.onchange('employee_id')
    def onchange_employee(self):
        super(TravelRequest, self).onchange_employee()
        self.customer_id = self.employee_id.customer_id.id
        self.area_id = self.employee_id.area_id.id
        return

    @api.depends('line_ids.reservation')
    def _get_reservation(self):
        for row in self:
            row.reservation = 'company' if row.line_ids.filtered(lambda l: l.reservation == 'company') else False

    def _get_mail_reminder(self):
        for row in self:
            mail_str = ''
            params = self.env['ir.config_parameter'].sudo()
            declaration_reminder_user_ids = params.get_param('declaration_reminder_user_id', default=False)
            if declaration_reminder_user_ids:
                for line in literal_eval(declaration_reminder_user_ids):
                    user_ids = self.env['res.users'].browse(line)
                    mail_str = mail_str + user_ids.email + ', '

            row.mail_reminder = mail_str

    @api.model
    def _reminder_send_email(self):
        params = self.env['ir.config_parameter'].sudo()
        notification_1 = int(params.get_param('declaration_reminder_1'))
        notification_2 = int(params.get_param('declaration_reminder_2'))
        notification_3 = int(params.get_param('declaration_reminder_3'))
        timezone = self._context.get('tz') or self.env.user.partner_id.tz or 'UTC'
        self_tz = self.with_context(tz=timezone)
        today = (datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
        today = fields.Datetime.context_timestamp(self_tz, fields.Datetime.from_string(today))
        today = datetime.strftime(today, '%Y-%m-%d %H:%M:%S')
        today = datetime.strptime(today, '%Y-%m-%d %H:%M:%S')

        template = self.env.ref('bi_employee_travel_dev.travel_advance_declaration_reminder', False)
        if not template:
            raise UserError(_('The email template is not defined.'))
        email_cc_org = template.email_cc

        if notification_1:
            notification_1 = (today - timedelta(days=notification_1)).strftime('%Y-%m-%d %H:%M:%S')
            notification_1 = datetime.strptime(notification_1, '%Y-%m-%d %H:%M:%S')
            notification_1a = notification_1.replace(hour=00, minute=00, second=00)
            notification_1b = notification_1.replace(hour=23, minute=59, second=59)
            notification_1a = notification_1a.strftime('%Y-%m-%d %H:%M:%S')
            notification_1b = notification_1b.strftime('%Y-%m-%d %H:%M:%S')

            expense_1 = self.env['travel.request'].search(
                [('return_date', '>=', notification_1a), ('return_date', '<=', notification_1b),
                 ('state', '=', 'approved')])
            for exp_1 in expense_1:
                template.send_mail(exp_1.id, force_send=True)
                exp_1.cnt_reminder += 1
                exp_1.last_reminder = today.date()

        if notification_2:
            notification_2 = (today - timedelta(days=notification_2)).strftime('%Y-%m-%d %H:%M:%S')
            notification_2 = datetime.strptime(notification_2, '%Y-%m-%d %H:%M:%S')
            notification_2a = notification_2.replace(hour=00, minute=00, second=00)
            notification_2b = notification_2.replace(hour=23, minute=59, second=59)
            notification_2a = notification_2a.strftime('%Y-%m-%d %H:%M:%S')
            notification_2b = notification_2b.strftime('%Y-%m-%d %H:%M:%S')

            expense_2 = self.env['travel.request'].search(
                [('return_date', '>=', notification_2a), ('return_date', '<=', notification_2b),
                 ('state', '=', 'approved')])
            for exp_2 in expense_2:
                template.send_mail(exp_2.id, force_send=True)
                exp_2.cnt_reminder += 1
                exp_2.last_reminder = today.date()

        if notification_3:
            notification_3 = (today - timedelta(days=notification_3)).strftime('%Y-%m-%d %H:%M:%S')
            notification_3 = datetime.strptime(notification_3, '%Y-%m-%d %H:%M:%S')
            # notification_3a = notification_3.replace(hour=00, minute=00, second=00)
            notification_3b = notification_3.replace(hour=23, minute=59, second=59)
            # notification_3a = notification_3a.strftime('%Y-%m-%d %H:%M:%S')
            notification_3b = notification_3b.strftime('%Y-%m-%d %H:%M:%S')

            expense_3 = self.env['travel.request'].search(
                [('return_date', '<=', notification_3b), ('state', '=', 'approved')])
            for exp_3 in expense_3:
                email_cc = email_cc_org
                if exp_3.employee_id.parent_id.work_email:
                    email_cc += exp_3.employee_id.parent_id.work_email
                template.email_cc = email_cc
                template.send_mail(exp_3.id, force_send=True)
                exp_3.cnt_reminder += 1
                exp_3.last_reminder = today.date()

        template.email_cc = email_cc_org

    def _get_reminder_data(self):
        self.return_date_str = self.return_date.strftime('%d-%B-%Y')
        self.nilai_advance_str = f'{self.nilai_advance:,}'

    @api.depends('line_ids.req_departure_date', 'line_ids.from_area_id', 'line_ids.to_area_id',
                 'line_ids.req_return_date')
    def _get_departure_date(self):
        for row in self:
            n = 1
            area = False
            for line in row.line_ids:
                if n == 1:
                    row.departure_date = line.req_departure_date
                    row.from_area = line.from_area_id.name

                row.return_date = line.req_return_date
                if area:
                    area = str(area) + ' & ' + str(line.to_area_id.name)
                else:
                    area = str(line.to_area_id.name)
                n += 1
            row.to_area = area

    def _get_uang_muka(self):
        for row in self:
            total_dp = 0
            total_amount = 0
            for line in row.advance_ids:
                total_dp += line.unit_amount
                total_amount += line.total_amount

            row.total_dp = total_dp
            row.nilai_advance = total_amount

    # @api.onchange('travel_type_id','customer_id')
    # def onchange_travel_type_id(self):
    #     if self.travel_type_id and self.customer_id:
    #         if not self.name:
    #             seq = self.env['ir.sequence'].next_by_code('travel.request.seq')
    #             seq = seq.replace('TRV-JOBSITE', str(self.travel_type_id.name))
    #             seq = seq.replace('PAMA',str(self.customer_user_id.name))
    #         else:
    #             try :
    #                 numbers = self.name.split('/')
    #                 numbers[1] = self.travel_type_id.name
    #                 seq = '/'.join(numbers)
    #             except:
    #                 seq = self.name
    #
    #         self.name = seq

    def return_from_trip(self):
        self.write({'state': 'returned'})
        # id_lst = []
        # for line in self.advance_ids :
        #     id_lst.append(line.id)
        # self.expense_ids = [(6,0,id_lst)]
        return

    def unlink(self):
        if any(self.filtered(lambda payslip: payslip.state not in ('draft'))):
            raise UserError(_('You cannot delete a travel request which is not draft!'))
        for row in self:
            for adv in row.advance_ids:
                if adv.state not in 'draft,refused' or adv.sheet_id:
                    raise UserError(
                        _('You cannot delete an advance payment which is not draft or refused or already has sheet!'))

            for exp in row.expense_ids:
                if exp.state not in 'draft,refused' or exp.sheet_id:
                    raise UserError(
                        _('You cannot delete an expense which is not draft or refused or already has sheet!'))
        return super(TravelRequest, self).unlink()

    def action_hr_expense_sheet(self):
        return {
            'name': 'Expense',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'context': {},
            'res_model': 'hr.expense.sheet',
            'domain': [('id', 'in', self.expense_ids.sheet_id.ids)],
        }

    def action_create_expense(self):
        id_lst = []
        for line in self.expense_ids:
            id_lst.append(line.id)

        advance_sheet_id = False
        for adv in self.expense_ids:
            sheet = self.env['hr.expense.sheet'].search(
                [('name', '=', adv.name), ('advance', '=', True), ('clearing_residual', '>', 0)])
            for sh in sheet:
                advance_sheet_id = sh.id

        val_exp = {
            'name': self.name,
            'employee_id': self.employee_id.id,
            'travel_expense': True,
            'advance_sheet_id': advance_sheet_id,
            'expense_line_ids': [(6, 0, id_lst)],
            'journal_id': self.env['ir.config_parameter'].sudo().get_param('expense_journal_id', False)
        }

        res = self.env['hr.expense.sheet'].create(val_exp)

        self.expense_sheet_id = res.id
        self.write({'state': 'submitted'})

        return

    @api.model
    def create(self, vals):
        if self.env['ir.config_parameter'].sudo().get_param('disallow_multi_travel', default=False) == 'True':
            if len(self.env['travel.request'].search(
                    [('employee_id', '=', vals['employee_id']), ('state', '!=', 'submitted')])) > 0:
                raise UserError(_('Employee %s has previous travel request where not done yet!' % self.env[
                    'hr.employee'].sudo().browse(vals['employee_id']).name))
        if 'name' not in vals or vals['name'] == False:
            vals['name'] = self.env['ir.sequence'].next_by_code('travel.request.seq')
        return super(TravelRequest, self).create(vals)


class My_travel_request_line(models.Model):
    _name = "travel.request.line"
    _description = "Travel Request Line"

    travel_line_id = fields.Many2one('travel.request', string="Travel Request", ondelete="cascade")
    from_area_id = fields.Many2one('res.area', required=True)
    to_area_id = fields.Many2one('res.area', required=True)
    req_departure_date = fields.Datetime(string="Departure Date", required=True)
    req_return_date = fields.Datetime(string="Return Date")
    # req_departure_date = fields.Date(string='Departure Date')
    days = fields.Char('Days', compute="_compute_days")
    req_travel_mode_id = fields.Many2one('travel.mode', string="Departure Mode")
    return_mode_id = fields.Many2one('travel.mode', string="Return Mode")
    reservation = fields.Selection([('company', 'Company'), ('employee', 'Employee')], string="Reservation")
    travel_status = fields.Selection([('single', 'Single'), ('family', 'Family')], string="Travel Status",
                                     default='single')
    travel_adult = fields.Integer('Adult', default=1)
    travel_child = fields.Integer('Child', default=0)
    travel_infant = fields.Integer('Infant', default=0)
    travel_passenger = fields.Integer('Passenger', compute='_get_total_passenger')

    @api.onchange('travel_adult', 'travel_child', 'travel_infant')
    def _get_total_passenger(self):
        for line in self:
            line.travel_passenger = line.travel_adult + line.travel_child + line.travel_infant

    @api.depends('req_departure_date', 'req_return_date')
    def _compute_days(self):
        for line in self:
            line.days = False
            if line.req_departure_date and line.req_return_date:
                diff = line.req_return_date - line.req_departure_date
                mini = diff.seconds // 60
                hour = mini // 60
                sec = (diff.seconds) - (mini * 60)
                miniute = mini - (hour * 60)
                time = str(diff.days) + ' Days, ' + ("%d:%02d.%02d" % (hour, miniute, sec))
                line.days = time
        return
