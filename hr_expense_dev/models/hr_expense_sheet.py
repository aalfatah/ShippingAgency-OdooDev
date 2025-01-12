from odoo import fields, models, api, _
from datetime import date, timedelta, datetime
from odoo.tools import email_split, float_is_zero
from odoo.exceptions import UserError, ValidationError


class ExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    # benefit_type_id = fields.Many2one('hr.benefit.type', string='Benefit Type', readonly=True, states={'draft': [('readonly', False)]},)
    # show_area = fields.Boolean(related='benefit_type_id.show_area')
    # show_accommodation = fields.Boolean(related='benefit_type_id.show_accommodation')
    # show_family_member = fields.Boolean(related='benefit_type_id.show_family_member')
    # request_date = fields.Date(string='Request Date', readonly=True, states={'draft': [('readonly', False)]},)
    # start_date = fields.Date(string='Start Date')
    # end_date = fields.Date(string='End Date')
    # duration = fields.Integer('Duration', compute="get_duration", readonly=False)
    # area_kerja_id = fields.Many2one('hr.employee.area', string='Area Kerja')
    # accommodation = fields.Selection([('mess','Mess'), ('house','House'),('no','No Accommodation')])
    # request_amount = fields.Float(string="Request Amount", compute="get_request_amount", readonly=False)
    # request_amount = fields.Float(string="Request Amount") #, required=True)
    # status_penempatan = fields.Selection([('lokal','LOKAL'),('mutasi','MUTASI')], related='employee_id.status_penempatan')
    # point_of_hire = fields.Char(string ='Asal Penerimaan', related='employee_id.point_of_hire')
    # alokasi_pembebanan = fields.Selection([('cabang','CABANG'),('ho','HO'),('site','SITE')], related='employee_id.alokasi_pembebanan')
    # description = fields.Text(string="Description")
    # housing_allotment = fields.Selection([('support','Support'), ('backoffice','Backoffice')], string="Housing Class", related='employee_id.housing_allotment')
    # family_id = fields.Many2one('hr.employee.family', string='Family')
    # family_info = fields.Char(string='Family Info')
    # area_id = fields.Many2one('hr.employee.area', string='Area', related='employee_id.area_id', store=True)
    # sub_area_id = fields.Many2one('hr.employee.area.sub', string='Sub Area', related='employee_id.sub_area_id', store=True)
    # customer_id = fields.Many2one('res.partner', string='Customer', related='employee_id.customer_id', store=True)
    # customer_user_id = fields.Many2one('res.partner', string='Customer User', related='employee_id.customer_user_id', store=True)

    # def action_submit_sheet(self):
        # emp = self.env['hr.employee'].sudo().search([('id','=',self.employee_id.id)])
        # emp.write({'marital': 'married'})
    #     self.write({'state': 'submit'})
    #     self.activity_update()

    # def action_sheet_move_create(self):
    #     res = super().action_sheet_move_create()
    #     if self.benefit_type_id.update_marital_status:
    #         emp = self.env['hr.employee'].sudo().search([('id', '=', self.employee_id.id)])
    #         emp.write({'marital': 'married'})
    #     return res

    # def action_cancel(self):
    #     if self.benefit_type_id.update_marital_status:
    #         emp = self.env['hr.employee'].sudo().search([('id','=',self.employee_id.id)])
    #         emp.write({'marital': 'single'})
    #
    #     for sheet in self:
    #         account_move = sheet.account_move_id
    #         sheet.account_move_id = False
    #         payments = self.env["account.payment"].search(
    #             [("expense_sheet_id", "=", sheet.id), ("state", "!=", "cancelled")]
    #         )
    #         # case : cancel invoice from hr_expense
    #         self._remove_reconcile_hr_invoice(account_move)
    #         # If the sheet is paid then remove payments
    #         if sheet.state == "done":
    #             if sheet.expense_line_ids[:1].payment_mode == "own_account":
    #                 self._remove_move_reconcile(payments, account_move)
    #                 self._cancel_payments(payments)
    #             else:
    #                 # In this case, during the cancellation the journal entry
    #                 # will be deleted
    #                 self._cancel_payments(payments)
    #         # Deleting the Journal entry if in the previous steps
    #         # (if the expense sheet is paid and payment_mode == 'own_account')
    #         # it has not been deleted
    #         if account_move.exists():
    #             if account_move.state != "draft":
    #                 account_move.button_cancel()
    #             account_move.with_context({"force_delete": True}).unlink()
    #         sheet.state = "submit"

    # @api.depends('benefit_type_id','area_kerja_id','duration')
    # def get_request_amount(self):
    #     request_amount = 0
    #     budget = self.env['hr.benefit.budget'].sudo().search([('area_id','=',self.area_kerja_id.id),('benefit_type_id','=',self.benefit_type_id.id),('housing_allotment','=',self.housing_allotment)],limit=1).amount
    #     request_amount = float(budget) * float(self.duration)
    #     self.request_amount = request_amount

    # @api.depends('end_date', 'start_date')
    # def get_duration(self):
    #     duration = 0
    #     if self.end_date and self.start_date:
    #         duration = (int(self.end_date.month) - int(self.start_date.month)) + 1
    #     self.duration = duration

    # @api.onchange('benefit_type_id','employee_id')
    # def onchange_benefit_type_id(self):
    #     if self.benefit_type_id.show_area and self.employee_id.id:
    #         self.area_kerja_id = self.employee_id.area_id.id
    #         for line in self.expense_line_ids:
    #             line.employee_id = self.employee_id.id
    #     else:
    #         self.area_kerja_id = False
    #     # self.payment_mode = self.benefit_type_id.payment_method
    #     if self.number == '/' or  self.number == False :
    #         number = self.env["ir.sequence"].next_by_code("hr.expense.sheet")
    #     else:
    #         number = self.number
    #     if self.benefit_type_id:
    #         code = self.env['hr.benefit.type'].sudo().search([('id','=',self.benefit_type_id.id)],limit=1).code
    #         benefit_code = str(code)
    #         str_code = number[5:9]
    #         number = number.replace(str_code, benefit_code)
    #         if self.employee_id:
    #             self.name = '%s %s' % (self.benefit_type_id.name, self.employee_id.name)
    #     self.number = number

    # def set_benefit_line(self, vals):
    #     if self.expense_line_ids:
    #         line = self.expense_line_ids[0]
    #         if 'benefit_type_id' in vals:
    #             benefit_type = self.env['hr.benefit.type'].browse(vals['benefit_type_id'])
    #             product_id = benefit_type.product_id.id
    #             benefit_type_name = benefit_type.name
    #         else:
    #             product_id = self.benefit_type_id.product_id.id
    #             benefit_type_name = self.benefit_type_id.name
    #         if 'employee_id' in vals:
    #             employee = self.env['hr.employee'].browse(vals['employee_id'])
    #         else:
    #             employee = self.employee_id
    #         line['date'] = vals.get('request_date', self.request_date)
    #         line['product_id'] = product_id
    #         line['name'] = "%s %s" % (benefit_type_name, employee.name)
    #         line['unit_amount'] = vals.get('request_amount', self.request_amount)
    #         line['payment_mode'] = vals.get('payment_mode', self.payment_mode)
    #     else:
    #         self.expense_line_ids.create({
    #             'date': vals.get('request_date', self.request_date),
    #             'product_id': self.benefit_type_id.product_id.id,
    #             'name': "%s %s" % (self.benefit_type_id.name, self.employee_id.name),
    #             'unit_amount': vals.get('request_amount', self.request_amount),
    #             'payment_mode': vals.get('payment_mode', self.payment_mode),
    #             'employee_id': self.employee_id.id,
    #             'sheet_id': self.id
    #         })

    # @api.model
    # def create(self, vals):
    #     sheet = super(HrExpenseSheetTBD, self).create(vals)
    #     if 'benefit_type_id' in vals:
    #         sheet.set_benefit_line(vals)
    #     return sheet
    #
    # def write(self, vals):
    #     if self.benefit_type_id.id:
    #         self.set_benefit_line(vals)
    #     return super(HrExpenseSheetTBD, self).write(vals)
