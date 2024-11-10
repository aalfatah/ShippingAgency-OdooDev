from odoo import http
from odoo.http import content_disposition, request
import io
import xlsxwriter


class ExcelReportController(http.Controller):
    @http.route(['/excel_payslip/<int:payslip_run_id>', ], type='http', auth="user", csrf=False)
    def get_excel_report(self, payslip_run_id, wizard=None, **args):
        payslip_run = request.env['hr.payslip.run'].search([('id', '=', payslip_run_id)])
        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('Payslips - %s' % payslip_run.name + '.xlsx'))
            ]
        )

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        title_style = workbook.add_format({'font_name': 'Times', 'font_size': 14, 'bold': True, 'align': 'center'})
        form_style = workbook.add_format(
            {'font_name': 'Times', 'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'left'})
        header_style = workbook.add_format(
            {'font_name': 'Times', 'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'center'})
        text_style = workbook.add_format(
            {'font_name': 'Times', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'left'})
        number_style = workbook.add_format(
            {'font_name': 'Times', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'right'})
        currency_format = workbook.add_format(
            {'num_format': '#,##0.00', 'font_name': 'Times', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1,
             'align': 'right'})
        date_format = workbook.add_format(
            {'num_format': 'd-mmm-yyyy', 'font_name': 'Times', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1,
             'align': 'left'})
        total_style = workbook.add_format(
            {'font_name': 'Times', 'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'right'})
        total_currency_format = workbook.add_format(
            {'num_format': '#,##0.00', 'font_name': 'Times', 'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1,
             'align': 'right'})

        struct_ids = request.env['hr.payslip'].search([('payslip_run_id', '=', payslip_run_id)]).mapped('struct_id')
        payroll_struc = request.env['hr.payroll.structure'].search([('id', 'in', struct_ids.ids)])
        for struct in payroll_struc:
            sheet = workbook.add_worksheet(struct.name)
            sheet.set_landscape()
            sheet.set_paper(9)
            sheet.set_margins(0.5, 0.5, 0.5, 0.5)
            sheet.set_column('B:AP', 20)
            sheet.write(0, 0, 'NO', header_style)
            sheet.write(0, 1, 'NRP', header_style)
            sheet.write(0, 2, 'NAMA', header_style)
            sheet.write(0, 3, 'DEPARTMENT', header_style)
            sheet.write(0, 4, 'PTKP', header_style)

            row = 1
            n = 1
            payslips = request.env['hr.payslip'].search([('payslip_run_id', '=', payslip_run_id), ('struct_id', '=', struct.id)])
            dict_total = {}
            last_col = 0
            for line in payslips:
                col = 5
                arr_total = []
                p = 0
                sheet.write(row, 0, row, number_style)
                sheet.write(row, 1, line.employee_id.nrp, number_style)
                sheet.write(row, 2, line.employee_id.name, text_style)
                sheet.write(row, 3, line.employee_id.department_id.name, text_style)
                sheet.write(row, 4, line.employee_id.ptkp_id.name, text_style)

                for line_ids in line.line_ids:
                    sheet.write(0, col, line_ids.name, header_style)
                    sheet.write(row, col, line_ids.total, currency_format)
                    arr_total.append(line_ids.total)

                    col += 1
                    p += 1
                    last_col = col

                if col == 6:
                    col = last_col

                sheet.write(0, col, 'ACC Number', header_style)
                sheet.write(row, col, line.employee_id.bank_account_id.acc_number, text_style)
                col += 1
                sheet.write(0, col, 'Bank', header_style)
                sheet.write(row, col, line.employee_id.bank_account_id.bank_id.name, text_style)
                col += 1

                dict_total[n] = arr_total
                n += 1
                row += 1

            arr_sub_total = []

            j = 0
            while j < p:
                total_1 = 0
                for dic in dict_total:
                    if dict_total[dic]:
                        total_1 += dict_total[dic][j]

                arr_sub_total.append(total_1)
                j += 1

            sheet.merge_range(row, 0, row, 4, 'TOTAL : ', total_style)
            col = 5
            m = 0
            for line_ids in line.line_ids:
                sheet.write(row, col, arr_sub_total[m], total_currency_format)
                col += 1
                m += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

        return response
