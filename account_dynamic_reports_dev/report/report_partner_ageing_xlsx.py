# _*_ coding: utf-8
from odoo import models, fields, api,_

from datetime import datetime
try:
    from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
    from xlsxwriter.utility import xl_rowcol_to_cell
except ImportError:
    ReportXlsx = object

class InsPartnerAgeingXlsx(models.AbstractModel):
    _name = 'report.account_dynamic_reports_dev.ins_partner_ageing_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def prepare_report_contents(self, data, period_dict, period_list, ageing_lines, filters, record,sheet,workbook):
        format_title = workbook.add_format({'bold': True,'align': 'center','font_size': 14,'font':'Arial'})
        format_header = workbook.add_format({'bold': True,'font_size': 11,'align': 'center','font': 'Arial'})
        format_header_left = workbook.add_format({'bold': True,'font_size': 11,'align': 'left','font': 'Arial'})
        format_header_period = workbook.add_format({'bold': True,'font_size': 11,'align': 'center','font': 'Arial','left': True,'right': True})
        content_header = workbook.add_format({'bold': False,'font_size': 10,'align': 'center','font': 'Arial'})
        content_header_date = workbook.add_format({'bold': False,'font_size': 10,'align': 'center','font': 'Arial'})
        line_header = workbook.add_format({'font_size': 11,'align': 'center','bold': True,'left': True,'right': True,'font': 'Arial'})
        line_header_left = workbook.add_format({'font_size': 11,'align': 'left','bold': True,'left': True,'border': True,'font': 'Arial'})
        line_header_total = workbook.add_format({'font_size': 11,'align': 'center','bold': True,'border': True,'font': 'Arial'})
        line_header_period = workbook.add_format({'font_size': 11,'align': 'center','bold': True,'left': True,'right': True,'font': 'Arial'})
        line_header_light = workbook.add_format({'bold': False,'font_size': 10,'align': 'center','border': False,'font': 'Arial','text_wrap': True,})
        line_header_light_period = workbook.add_format({'bold': False,'font_size': 10,'align': 'center','left': True,'right': True,'font': 'Arial','text_wrap': True,})
        line_header_light_date = workbook.add_format({'bold': False,'font_size': 10,'border': False,'font': 'Arial','align': 'center','num_format': 'YYYY-MM-DD'})
        date_format = workbook.add_format({'num_format': 'd-mmm-yyyy','font_name': 'Times', 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'center'})
        line_header_30 = workbook.add_format({'font_size': 11,'align': 'center','bold': True,'left': True,'right': True,'font': 'Arial'})
        line_header_30.set_bg_color('#f3e975')
        line_header_60 = workbook.add_format({'font_size': 11,'align': 'center','bold': True,'left': True,'right': True,'font': 'Arial'})
        line_header_60.set_bg_color('#ecb0b0')
        line_header_light_period_30 = workbook.add_format({'bold': False,'font_size': 10,'align': 'center','left': True,'right': True,'font': 'Arial','text_wrap': True,})
        line_header_light_period_30.set_bg_color('#f3e975')
        line_header_light_period_60 = workbook.add_format({'bold': False,'font_size': 10,'align': 'center','left': True,'right': True,'font': 'Arial','text_wrap': True,})
        line_header_light_period_60.set_bg_color('#ecb0b0')

        data = data[0]
        row_pos = 3

        if record.include_details:
            sheet.write_string(row_pos, 0,  _('Entry #'), format_header)
            sheet.write_string(row_pos, 1, _('Due Date'), format_header)
            sheet.write_string(row_pos, 2, _('Journal'), format_header)
            sheet.write_string(row_pos, 3, _('Account'), format_header)
        else:
            sheet.merge_range(row_pos, 0, row_pos, 3, _('Partner'),format_header)

        sheet.write_string(row_pos, 4, _('Total'), format_header)
        k = 5
        if filters['display_currency'] :
            sheet.write_string(row_pos, k, _('%'),format_header)
            k += 1

        for period in period_list:
            sheet.write_string(row_pos, k, str(period),format_header_period)
            k += 1

        # sheet.write_string(row_pos, k, _('Total Header'),format_header_period)
        

        if ageing_lines:
            for line in ageing_lines:
                row_pos += 1
                sheet.write_string(row_pos, 5, '', line_header_light_period)
                sheet.write_string(row_pos, 6, '', line_header_light_period)
                sheet.write_string(row_pos, 7, '', line_header_light_period)
                sheet.write_string(row_pos, 8, '', line_header_light_period)
                sheet.write_string(row_pos, 9, '', line_header_light_period)

                row_pos += 1
                if line != 'Total':
                    sheet.merge_range(row_pos, 0, row_pos, 3, ageing_lines[line].get('partner_name'), line_header)
                    sheet.write_number(row_pos, 4, ageing_lines[line]['total'], line_header)
                    if filters['display_currency'] :
                        sheet.write_number(row_pos, 5, ageing_lines[line]['percentage'], line_header_light_period)

                else:
                    sheet.merge_range(row_pos, 0, row_pos, 3, _('Total'),line_header_total)
                    k += 1
                    sheet.write_number(row_pos, 4, ageing_lines[line]['total'], line_header_total)
                    if filters['display_currency'] :
                        sheet.write_number(row_pos, 5, ageing_lines[line]['percentage_total'], line_header_total)


                k = 5
                if filters['display_currency'] :
                    k += 1
                for period in period_list:
                    if line != 'Total':
                        if period == '31 - 60':
                            sheet.write_number(row_pos, k, ageing_lines[line][period],line_header_30)
                        elif period == '61 - 90' or period == '90 +':
                            sheet.write_number(row_pos, k, ageing_lines[line][period],line_header_60)
                        else:
                            sheet.write_number(row_pos, k, ageing_lines[line][period],line_header)
                    else:
                        sheet.write_number(row_pos, k, ageing_lines[line][period], line_header_total)
                    k += 1

                

                if record.include_details:
                    if line != 'Total':
                        count, offset, sub_lines, period_list = record.process_detailed_data(partner=line, fetch_range=1000000)
                        for sub_line in sub_lines:
                            row_pos += 1
                            sheet.write_string(row_pos, 0, sub_line.get('move_name') or '',line_header_light)
                            sheet.write_datetime(row_pos, 1, sub_line.get('date_maturity'),line_header_light_date)
                            sheet.write_string(row_pos, 2, sub_line.get('journal_name'),line_header_light)
                            sheet.write_string(row_pos, 3, sub_line.get('account_name') or '',line_header_light)
                            sheet.write_string(row_pos, 4,'', line_header_light_period)
                            k = 5
                            if filters['display_currency'] :
                                sheet.write_string(row_pos, 5,'', line_header_light_period)
                                k += 1

                            sheet.write_number(row_pos, k,float(sub_line.get('range_0')), line_header_light_period)
                            k += 1
                            sheet.write_number(row_pos, k,float(sub_line.get('range_1')), line_header_light_period)
                            k += 1
                            sheet.write_number(row_pos, k,float(sub_line.get('range_2')), line_header_light_period_30)
                            k += 1
                            sheet.write_number(row_pos, k,float(sub_line.get('range_3')), line_header_light_period_60)
                            k += 1
                            sheet.write_number(row_pos, k,float(sub_line.get('range_6')), line_header_light_period_60)

            row_pos += 1
            k = 5

    def generate_xlsx_report(self, workbook, data, record):
        row_pos = 0
        sheet = workbook.add_worksheet('Partner Ageing')
        sheet.set_column(0, 0, 15)
        sheet.set_column(1, 1, 12)
        sheet.set_column(2, 2, 15)
        sheet.set_column(3, 3, 25)
        sheet.set_column(4, 4, 15)
        sheet.set_column(5, 5, 15)
        sheet.set_column(6, 6, 15)
        sheet.set_column(7, 7, 15)
        sheet.set_column(8, 8, 15)
        sheet.set_column(9, 9, 15)
        sheet.set_column(10, 10, 15)
        sheet.freeze_panes(4, 0)
        sheet.screen_gridlines = False
        sheet.set_zoom(75)

        record = record
        if record:
            data = record.read()
            sheet.merge_range(0, 0, 0, 9, 'Partner Ageing'+' - '+data[0]['company_id'][1])
            dateformat = self.env.user.lang
            filters, ageing_lines, period_dict, period_list, sub_line = record.get_report_datas()
            self.prepare_report_contents(data, period_dict, period_list, ageing_lines, filters,record,sheet,workbook)
