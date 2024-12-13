from odoo import http
from odoo.http import content_disposition, request
import io
import xlsxwriter
    


class ExcelReportController(http.Controller):
    @http.route(['/excel_report/<int:tax_status_id>',], type='http', auth="user", csrf=False)
    def get_excel_report(self,tax_status_id,wizard=None,**args):
        tax = request.env['employee.tax.status'].search([('id','=',tax_status_id)])
        response = request.make_response(
                    None,
                    headers=[
                        ('Content-Type', 'application/vnd.ms-excel'),
                        ('Content-Disposition', content_disposition('Employee Tax Status - %s' % tax.name + '.xlsx'))
                    ]
                )

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        title_style = workbook.add_format({'font_name': 'Times', 'font_size': 14, 'bold': True, 'align': 'center'})
        form_style = workbook.add_format({'font_name': 'Times', 'bold': True, 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'left'})
        header_style = workbook.add_format({'font_name': 'Times', 'bold': True, 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'center'})
        text_style = workbook.add_format({'font_name': 'Times', 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'left'})
        number_style = workbook.add_format({'font_name': 'Times', 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'right'})
        date_format = workbook.add_format({'num_format': 'd-mmm-yyyy','font_name': 'Times', 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'left'})

        sheet = workbook.add_worksheet('Tax Status')
        sheet.set_landscape()
        sheet.set_paper(9)
        sheet.set_margins(0.5,0.5,0.5,0.5)
        sheet.set_column('A:A', 7)
        sheet.set_column('B:B', 40)
        sheet.set_column('C:E', 15)
        sheet.merge_range('B1:E1', 'Employee Tax Status', title_style)
        sheet.write(2, 0, 'Name', form_style)
        sheet.write(3, 0, 'Date', form_style)
        sheet.write(4, 0, 'Remark', form_style)
        sheet.merge_range('B3:E3', tax.name, text_style)
        sheet.merge_range('B4:E4', tax.date, date_format)

        if tax.remarks:
            sheet.merge_range('B5:E5', tax.remarks, text_style)
        else:
            sheet.merge_range('B5:E5', '', text_style)

        sheet.write(6, 0, 'No.', header_style)
        sheet.write(6, 1, 'Employee', header_style)
        sheet.write(6, 2, 'Family Status', header_style)
        sheet.write(6, 3, 'Tax Status Prev', header_style)
        sheet.write(6, 4, 'Tax Status', header_style)

        row = 7
        number = 1

        if tax.tax_change_only :
            lines = request.env['employee.tax.status.line'].search([('tax_status_id','=',tax_status_id),('updated','=',True)])
        else:
            lines = request.env['employee.tax.status.line'].search([('tax_status_id','=',tax_status_id)])

        for line in lines:
            name = line.employee_id.name
            tax_status_prev = line.tax_status_prev.name
            tax_status = line.tax_status.name

            sheet.write(row, 0, number, text_style)
            sheet.write(row, 1, name, text_style)
            sheet.write(row, 2, line.family_status, text_style)
            sheet.write(row, 3, tax_status_prev, text_style)
            sheet.write(row, 4, tax_status, text_style)

            row += 1
            number += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

        return response