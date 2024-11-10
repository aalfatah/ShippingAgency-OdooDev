from odoo import api, fields, models, _
from datetime import date
from num2words import num2words


class HrContractTbd(models.Model):
    _inherit = 'hr.contract'

    # tunjangan_jabatan = fields.Monetary(string='Tunjangan Jabatan')
    # tunjangan_transport = fields.Monetary(string='Tunjangan Transport')
    # tunjangan_makan = fields.Monetary(string='Tunjangan Makan')

    days_exp = fields.Integer('Remaining Days', compute="get_days_expired", store=True)
    # terbilang = fields.Char(string="Terbilang", compute="_get_terbilang")
    # tunjangan_tetap_terbilang = fields.Char(string="Terbilang", compute="_get_terbilang")

    @api.depends('date_end', 'state')
    def get_days_expired(self):
        for contract in self:
            if contract.date_end:
                if contract == contract.employee_id.contract_id:
                    contract.days_exp = (contract.date_end - fields.Date.today()).days
                else:
                    contract.days_exp = 99999
            else:
                contract.days_exp = 99999
            if contract.state == 'open':
                self.env['hr.contract'].search([('employee_id', '=', contract.employee_id.id),
                                                ('days_exp', '!=', 9999),
                                                ('id', '!=', contract.id)]).update({'days_exp': 9999})

    def mail_reminder(self):
        today = date.today()
        # contract_email_template_id = False
        # for line in self.env['res.config.settings'].search([]):
        #     contract_email_template_id = line.contract_monitoring_mail_template_id
        # contract_email_template = contract_email_template_id
        contract_email_template = int(self.env['ir.config_parameter'].sudo().get_param('contract_monitoring_mail_template_id', default=False))
        # mailing = self.env['mail.template'].search([('id', '=', contract_email_template)])
        if contract_email_template:
            mailing = self.env['mail.template'].browse(contract_email_template)
            mail_server = mailing.mail_server_id.id
            if not mail_server:
                server = self.env['ir.mail_server'].search([], limit=1)
                mail_server = server.id

            line_60 = ''
            line_30 = ''
            line_14 = ''
            i60 = i30 = i14 = 0
            for row in self.env['hr.contract'].search([('state','=','open')]):
                if row.employee_id :
                    if row.days_exp > 30 and row.days_exp <= 60:
                        i60 = i60 + 1
                    line_60 = line_60 + "<tr><td style='text-align: right;'>" + str(i60) + '</td><td>' + str(row.employee_id.nrp) + '</td><td>' + str(row.employee_id.name) + '</td><td>' + str(row.name) + '</td><td>' + str(row.contract_type_id.name) + '</td><td>' + str(row.date_start.strftime('%d %b %Y')) + '</td><td>' + str(row.date_end.strftime('%d %b %Y'))+'</td></tr>'
                    if row.days_exp > 14 and row.days_exp <= 30:
                        i30 = i30 + 1
                        line_30 = line_30 + "<tr><td style='text-align: right;'>" + str(i30) + '</td><td>' + str(row.employee_id.nrp) + '</td><td>' + str(row.employee_id.name) + '</td><td>' + str(row.name) + '</td><td>' + str(row.contract_type_id.name) + '</td><td>' + str(row.date_start.strftime('%d %b %Y')) + '</td><td>' + str(row.date_end.strftime('%d %b %Y'))+'</td></tr>'
                    if row.days_exp > 0 and row.days_exp <= 14:
                        i14 = i14 + 1
                        line_14 = line_14 + "<tr><td style='text-align: right;'>" + str(i14) + '</td><td>' + str(row.employee_id.nrp) + '</td><td>' + str(row.employee_id.name) + '</td><td>' + str(row.name) + '</td><td>' + str(row.contract_type_id.name) + '</td><td>' + str(row.date_start.strftime('%d %b %Y')) + '</td><td>' + str(row.date_end.strftime('%d %b %Y'))+'</td></tr>'

            table_header = "<table class='table' style='font-size:10px;'><thead><tr><th>No.</th><th>NRP</th><th>Employee</th><th>Contract No.</th><th>Contract Type</th><th>Start Date</th><th>End Date</th></tr></thead>"
            body_html = "<div style='font-size:13px;font-family:&quot;Lucida Grande&quot;, Helvetica, Verdana, Arial, sans-serif;color: rgb(51, 55, 58); font-family: &quot;Open Sans&quot;, Arial, sans-serif; font-size: 18px; margin: 0px; padding: 0px;'> \
                                <span>1. Contract berakhir dalam 14 hari :</span><br/>" + table_header + str(line_14) +"</table><br/> \
                                <span>2. Contract berakhir dalam 30 hari :</span><br/>" + table_header + str(line_30) +"</table><br/> \
                                <span>3. Contract berakhir dalam 60 hari :</span><br/>" + table_header + str(line_60) +"</table><br/> \
                                <br/> Odoo\
                            </div>"

            main_content = {
                'subject': _('%s %s') % (mailing.subject, today.strftime('%d %b %Y')),
                'author_id': 3, # self.env.user.partner_id.id,
                'email_from': mailing.email_from,
                'body_html': mailing.body_html + body_html,
                'email_to': mailing.email_to, #.partner_to,
                'notification': False,
                'mail_server_id': mail_server,
            }
            self.env['mail.mail'].sudo().create(main_content).send()

    @api.model
    def update_state(self):
        contracts = self.env['hr.contract'].search([('state', 'in', ('open','close'))])
        for contract in contracts:
            contract.get_days_expired()
        employees = self.env['hr.employee'].search([('active','=',True)])
        for employee in employees:
            employee._get_contract_expiry_status()
            employee._status_karyawan()
        return super(HrContractTbd, self).update_state()

    # def _get_terbilang(self):
    #     for row in self:
    #         row.terbilang = (num2words(row.wage, lang="id").upper() + ' RUPIAH')
    #         row.tunjangan_tetap_terbilang = (num2words(row.tunjangan_tetap, lang="id").upper() + ' RUPIAH')
