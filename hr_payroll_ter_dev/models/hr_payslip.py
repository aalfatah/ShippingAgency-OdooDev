from odoo import api, fields, models, tools, _
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
import locale 
from num2words import num2words


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    ter = fields.Selection(string='TER', related='ptkp_id.ter')
