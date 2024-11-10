# -*- coding: utf-8 -*-

import datetime
from datetime import datetime
# from report_xlsx.report.report_xlsx import ReportXlsxAbstract
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo import api, fields, models, _


class InputStandardExcel(models.AbstractModel):
    _name = 'report.payroll_other_inputs.input_other_xlsx'
    _description = "report.payroll_other_inputs.input_other_xlsx"
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, employee):
        bold = workbook.add_format({'bold': True})
        middle = workbook.add_format({'bold': True, 'top': 1})
        left = workbook.add_format({'left': 1, 'top': 1, 'bold': True})
        right = workbook.add_format({'right': 1, 'top': 1})
        top = workbook.add_format({'top': 1})
        report_format = workbook.add_format({'font_size': 24})
        rounding = self.env.user.company_id.currency_id.decimal_places or 2
        lang_code = 'es_VE'
        date_format = self.env['res.lang']._lang_get(lang_code).date_format
        time_format = self.env['res.lang']._lang_get(lang_code).time_format
        locked = workbook.add_format({'locked': True}) 
        report = employee
        
        def get_datetime_format(date):
            if date:
                date = datetime.strptime(date, DEFAULT_SERVER_DATETIME_FORMAT)
                date = date.strftime(time_format)
            return date

        def get_date_format(date):
            if date:
                date = datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT)
                date = date.strftime(date_format)
            return date
        if employee:
            sheet = workbook.add_worksheet(report.rule_input_id.name +'_'+ str(report.date_from))
            head = [
                {'name': 'Identification',
                 'larg': 15,
                 'col': {}},
                {'name': 'Name',
                 'larg': 50,
                 'col': {}},
                {'name': 'Amount',
                 'larg': 15,
                 'col': {}},
            ]
            all_lines = report.employee_data_ids
            if all_lines:
                row = 0
                row += 1
                date_now = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                start_row = row
                for i, line in enumerate(all_lines):
                    i += row
                    sheet.write(i, 0, line.identification_id)
                    sheet.write(i, 1, line.name)
                    sheet.write(i, 2, 0)
                row = i
                for j, h in enumerate(head):
                    sheet.set_column(j, j, h['larg'])
                table = []
                for h in head:
                    col = {}
                    col['header'] = h['name']
                    col.update(h['col'])
                    table.append(col)
                sheet.add_table(start_row - 1, 0, row + 1, len(head) - 1,
                                {'total_row': 1,
                                 'columns': table,
                                 'style': 'Table Style Light 9',
                                 })
                sheet.set_row(0, 15, bold)
