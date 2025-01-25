from odoo import api, fields, models, _

FETCH_RANGE = 2000


class InsPartnerLedger(models.TransientModel):
    _inherit = "ins.partner.ledger"

    def process_data_invoice_list(self):
        '''
        It is the method for showing summary details of each accounts. Just basic details to show up
        Three sections,
        1. Initial Balance
        2. Current Balance
        3. Final Balance
        :return:
        '''
        cr = self.env.cr

        data = self.get_filters(default_filters={})

        WHERE = self.build_where_clause(data)

        partner_company_domain = [('parent_id', '=', False),
                                  '|',
                                  ('company_id', '=', self.env.company.id),
                                  ('company_id', '=', False)]
        if self.partner_category_ids:
            partner_company_domain.append(('category_id','in',self.partner_category_ids.ids))

        if data.get('partner_ids', []):
            partner_ids = self.env['res.partner'].browse(data.get('partner_ids'))
        else:
            partner_ids = self.env['res.partner'].search(partner_company_domain)

        move_lines = {
            x.id: {
                'name': x.name,
                'code': x.id,
                'company_currency_id': 0,
                'company_currency_symbol': 'AED',
                'company_currency_precision': 0.0100,
                'company_currency_position': 'after',
                'id': x.id,
                'lines': []
            } for x in partner_ids
        }
        for partner in partner_ids:

            currency = partner.company_id.currency_id or self.env.company.currency_id
            symbol = currency.symbol
            rounding = currency.rounding
            position = currency.position

            opening_balance = 0.0

            WHERE_INIT = WHERE + " AND l.date < '%s'" % data.get('date_from')
            WHERE_INIT += " AND l.partner_id = %s" % partner.id
            ORDER_BY_CURRENT = 'l.date'

            if data.get('initial_balance'):
                sql = ('''
                    SELECT 
                        COALESCE(SUM(l.debit),0) AS debit, 
                        COALESCE(SUM(l.credit),0) AS credit, 
                        COALESCE(SUM(l.debit - l.credit),0) AS balance
                    FROM account_move_line l
                    JOIN account_move m ON (l.move_id=m.id)
                    JOIN account_account a ON (l.account_id=a.id)
                    --LEFT JOIN account_account_type AS ty ON a.user_type_id = ty.id
                    --LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)
                    JOIN account_journal j ON (l.journal_id=j.id)
                    WHERE %s
                ''') % WHERE_INIT
                cr.execute(sql)
                for row in cr.dictfetchall():
                    row['move_name'] = 'Initial Balance'
                    row['partner_id'] = partner.id
                    row['initial_bal'] = True
                    row['ending_bal'] = False
                    opening_balance += row['balance']
                    move_lines[partner.id]['lines'].append(row)
            WHERE_CURRENT = WHERE + " AND l.date >= '%s'" % data.get('date_from') + " AND l.date <= '%s'" % data.get(
                'date_to')
            WHERE_CURRENT += " AND p.id = %s" % partner.id
            sql = ('''
                SELECT
                    l.id AS lid,
                    m.invoice_date AS ldate,
                    m.invoice_date_due AS ldate_due,
                    j.code AS lcode,
                    a.name AS account_name,
                    m.name AS move_name,
                    l.name AS lname,
                    m.state AS state,
                    m.state AS state,
                    COALESCE(l.debit,0) AS debit,
                    COALESCE(l.credit,0) AS credit,
                    COALESCE(l.balance,0) AS balance,
                    COALESCE(l.amount_currency,0) AS balance_currency
                FROM account_move_line l
                JOIN account_move m ON (l.move_id=m.id)
                JOIN account_account a ON (l.account_id=a.id)
                --LEFT JOIN account_account_type AS ty ON a.user_type_id = ty.id
                --LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                LEFT JOIN res_currency c ON (l.currency_id=c.id)
                LEFT JOIN res_currency cc ON (l.company_currency_id=cc.id)
                LEFT JOIN res_partner p ON (l.partner_id=p.id)
                JOIN account_journal j ON (l.journal_id=j.id)
                WHERE m.move_type = 'in_invoice' and %s
                --GROUP BY l.id, l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.id, m.name, c.rounding, cc.rounding, cc.position, c.position, c.symbol, cc.symbol, p.name
                ORDER BY %s
            ''') % (WHERE_CURRENT, ORDER_BY_CURRENT)
            cr.execute(sql)
            current_lines = cr.dictfetchall()
            for row in current_lines:
                row['initial_bal'] = False
                row['ending_bal'] = False

                current_balance = row['balance']
                row['balance'] = opening_balance + current_balance
                opening_balance += current_balance
                row['initial_bal'] = False

                move_lines[partner.id]['lines'].append(row)
            if data.get('initial_balance'):
                WHERE_FULL = WHERE + " AND l.date <= '%s'" % data.get('date_to')
            else:
                WHERE_FULL = WHERE + " AND l.date >= '%s'" % data.get('date_from') + " AND l.date <= '%s'" % data.get(
                    'date_to')
            WHERE_FULL += " AND p.id = %s" % partner.id
            sql = ('''
                SELECT 
                    COALESCE(SUM(l.debit),0) AS debit, 
                    COALESCE(SUM(l.credit),0) AS credit, 
                    COALESCE(SUM(l.debit - l.credit),0) AS balance
                FROM account_move_line l
                JOIN account_move m ON (l.move_id=m.id)
                JOIN account_account a ON (l.account_id=a.id)
                --LEFT JOIN account_account_type AS ty ON a.user_type_id = ty.id
                --LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                LEFT JOIN res_currency c ON (l.currency_id=c.id)
                LEFT JOIN res_partner p ON (l.partner_id=p.id)
                JOIN account_journal j ON (l.journal_id=j.id)
                WHERE %s
            ''') % WHERE_FULL
            cr.execute(sql)
            for row in cr.dictfetchall():
                if (data.get('display_accounts') == 'balance_not_zero' and currency.is_zero(row['debit'] - row['credit']))\
                        or (data.get('balance_less_than_zero') and (row['debit'] - row['credit']) > 0)\
                        or (data.get('balance_greater_than_zero') and (row['debit'] - row['credit']) < 0):
                    move_lines.pop(partner.id, None)
                else:
                    row['ending_bal'] = True
                    row['initial_bal'] = False
                    move_lines[partner.id]['lines'].append(row)
                    move_lines[partner.id]['debit'] = row['debit']
                    move_lines[partner.id]['credit'] = row['credit']
                    move_lines[partner.id]['balance'] = row['balance']
                    move_lines[partner.id]['company_currency_id'] = currency.id
                    move_lines[partner.id]['company_currency_symbol'] = symbol
                    move_lines[partner.id]['company_currency_precision'] = rounding
                    move_lines[partner.id]['company_currency_position'] = position
                    move_lines[partner.id]['count'] = len(current_lines)
                    move_lines[partner.id]['pages'] = self.get_page_list(len(current_lines))
                    move_lines[partner.id]['single_page'] = True if len(current_lines) <= FETCH_RANGE else False
        return move_lines

    def get_report_datas_invoice_list(self, default_filters={}):
        if self.validate_data():
            filters = self.process_filters()
            account_lines = self.process_data_invoice_list()
            return filters, account_lines

    def action_invoice_list_pdf(self):
        filters, account_lines = self.get_report_datas_invoice_list()
        return self.env.ref(
            'account_dynamic_reports_dev'
            '.action_print_invoice_list').with_context(landscape=True).report_action(
            self, data={'Ledger_data': account_lines,
                        'Filters': filters
                        })
