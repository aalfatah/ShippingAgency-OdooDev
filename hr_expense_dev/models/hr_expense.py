import re

from odoo import fields, models, Command, api, _
from odoo.tools.misc import clean_context, format_date
from odoo.tools import email_split, float_is_zero, float_repr, float_compare, is_html_empty
from odoo.exceptions import UserError, ValidationError
from collections import defaultdict


class Expense(models.Model):
    _inherit = 'hr.expense'

    def _get_default_expense_sheet_values(self):
        # If there is an expense with total_amount_company == 0, it means that expense has not been processed by OCR yet
        expenses_with_amount = self.filtered(lambda expense: not float_compare(expense.total_amount_company, 0.0, precision_rounding=(expense.company_currency_id or expense.currency_id).rounding) == 0)

        if any(expense.state != 'draft' or expense.sheet_id for expense in expenses_with_amount):
            raise UserError(_("You cannot report twice the same line!"))
        if not expenses_with_amount:
            raise UserError(_("You cannot report the expenses without amount!"))
        if len(expenses_with_amount.mapped('employee_id')) != 1:
            raise UserError(_("You cannot report expenses for different employees in the same report."))
        if any(not expense.product_id for expense in expenses_with_amount):
            raise UserError(_("You can not create report without category."))
        if len(self.company_id) != 1:
            raise UserError(_("You cannot report expenses for different companies in the same report."))
        if len(set(expenses_with_amount.mapped('advance'))) != 1:
            raise UserError(_("You cannot report cash advance and expenses in the same report."))

        # Check if two reports should be created
        own_expenses = expenses_with_amount.filtered(lambda x: x.payment_mode == 'own_account')
        company_expenses = expenses_with_amount - own_expenses
        create_two_reports = own_expenses and company_expenses

        sheets = [own_expenses, company_expenses] if create_two_reports else [expenses_with_amount]
        values = []

        # We use a fallback name only when several expense sheets are created,
        # else we use the form view required name to force the user to set a name
        for todo in sheets:
            paid_by = 'company' if todo[0].payment_mode == 'company_account' else 'employee'
            sheet_name = _("New Expense Report, paid by %(paid_by)s", paid_by=paid_by) if len(sheets) > 1 else False
            if len(todo) == 1:
                sheet_name = todo.name
            else:
                dates = todo.mapped('date')
                if False not in dates:  # If at least one date isn't set, we don't set a default name
                    min_date = format_date(self.env, min(dates))
                    max_date = format_date(self.env, max(dates))
                    if min_date == max_date:
                        sheet_name = min_date
                    else:
                        sheet_name = _("%(date_from)s - %(date_to)s", date_from=min_date, date_to=max_date)

            vals = {
                'company_id': self.company_id.id,
                'employee_id': self[0].employee_id.id,
                'name': sheet_name,
                'advance': list(set(expenses_with_amount.mapped('advance')))[0],
                'expense_line_ids': [Command.set(todo.ids)],
                'state': 'draft',
            }
            values.append(vals)
        return values

    unit_amount = fields.Float("Unit Price", compute='', store=True, required=True,
                               copy=True,
                               states={'draft': [('readonly', False)], 'reported': [('readonly', False)],
                                       'refused': [('readonly', False)]}, digits='Product Price')
    quantity = fields.Float(required=True, readonly=True,
                            states={'draft': [('readonly', False)], 'reported': [('readonly', False)],
                                    'refused': [('readonly', False)]}, digits='Product Unit of Measure', default=1)
    tax_ids = fields.Many2many('account.tax', 'expense_tax', 'expense_id', 'tax_id',
                               # compute='_compute_from_product_id_company_id', store=True, readonly=False,
                               domain="[('company_id', '=', company_id), ('type_tax_use', '=', 'purchase')]",
                               string='Taxes')
    untaxed_amount = fields.Float("Subtotal", store=True, compute='_compute_amount', digits='Account')
    total_amount = fields.Monetary("Total", compute='_compute_amount', store=True, currency_field='currency_id',
                                   tracking=True)
    amount_residual = fields.Monetary(string='Amount Due', compute='_compute_amount_residual', compute_sudo=True)
    company_currency_id = fields.Many2one('res.currency', string="Report Company Currency",
                                          related='sheet_id.currency_id', store=True, readonly=False)
    total_amount_company = fields.Monetary("Total (Company Currency)", compute='_compute_total_amount_company',
                                           store=True, currency_field='company_currency_id')
    analytic_account_ids = fields.Many2many("account.analytic.account", compute="_compute_analytic_account_ids", store=True)

    def _compute_analytic_account_ids(self):
        # Prefetch all involved analytic accounts
        with_distribution = self.filtered("analytic_distribution")
        batch_by_analytic_account = defaultdict(list)
        for record in with_distribution:
            for account_id in map(int, record.analytic_distribution):
                batch_by_analytic_account[account_id].append(record.id)
        existing_account_ids = set(
            self.env["account.analytic.account"]
            .browse(map(int, batch_by_analytic_account))
            .exists()
            .ids
        )
        # Store them
        self.analytic_account_ids = False
        for account_id, record_ids in batch_by_analytic_account.items():
            if account_id not in existing_account_ids:
                continue
            self.browse(record_ids).analytic_account_ids = [
                fields.Command.link(account_id)
            ]

    @api.depends('quantity', 'unit_amount', 'tax_ids', 'currency_id')
    def _compute_amount(self):
        for expense in self:
            expense.untaxed_amount = expense.unit_amount * expense.quantity
            taxes = expense.tax_ids.compute_all(expense.unit_amount, expense.currency_id, expense.quantity,
                                                expense.product_id, expense.employee_id.user_id.partner_id)
            expense.total_amount = taxes.get('total_included')

    # @api.depends('quantity', 'unit_amount', 'tax_ids', 'currency_id')
    # def _compute_amount(self):
    #     for expense in self:
    #         if not expense.product_has_cost:
    #             continue
    #         base_lines = [expense._convert_to_tax_base_line_dict(price_unit=expense.unit_amount, quantity=expense.quantity)]
    #         taxes_totals = self.env['account.tax']._compute_taxes(base_lines)['totals'][expense.currency_id]
    #         expense.total_amount = taxes_totals['amount_untaxed'] + taxes_totals['amount_tax']

    # @api.depends("sheet_id.account_move_id.line_ids")
    # def _compute_amount_residual(self):
    #     for expense in self:
    #         if not expense.sheet_id:
    #             expense.amount_residual = expense.total_amount
    #             continue
    #         if not expense.currency_id or expense.currency_id == expense.company_id.currency_id:
    #             residual_field = 'amount_residual'
    #         else:
    #             residual_field = 'amount_residual_currency'
    #         payment_term_lines = expense.sheet_id.account_move_id.line_ids \
    #             .filtered(
    #             lambda line: line.expense_id == expense and line.account_internal_type in ('receivable', 'payable'))
    #         expense.amount_residual = -sum(payment_term_lines.mapped(residual_field))

    # @api.depends("sheet_id.account_move_id.line_ids")
    # def _compute_amount_residual(self):
    #     for expense in self:
    #         if not expense.sheet_id:
    #             expense.amount_residual = expense.total_amount
    #             continue
    #         if not expense.currency_id or expense.currency_id == expense.company_currency_id:
    #             residual_field = 'amount_residual'
    #         else:
    #             residual_field = 'amount_residual_currency'
    #         payment_term_lines = expense.sheet_id.account_move_id.sudo().line_ids \
    #             .filtered(lambda line: line.expense_id == expense and line.account_type in ('asset_receivable', 'liability_payable'))
    #         expense.amount_residual = -sum(payment_term_lines.mapped(residual_field))

    # @api.depends('date', 'total_amount', 'company_currency_id')
    @api.depends('currency_rate', 'total_amount', 'tax_ids', 'product_id', 'employee_id.user_id.partner_id', 'quantity')
    def _compute_total_amount_company(self):
        for expense in self:
            amount = 0
            currency_id = expense.company_currency_id or expense.currency_id
            if currency_id:
                date_expense = expense.date
                amount = expense.currency_id._convert(
                    expense.total_amount, currency_id,
                    expense.company_id, date_expense or fields.Date.today())
            expense.total_amount_company = amount
            amount_tax_company = expense.currency_id._convert(
                expense.amount_tax, currency_id,
                expense.company_id, date_expense or fields.Date.today())
            expense.amount_tax_company = amount_tax_company

    # @api.depends('currency_rate', 'total_amount', 'tax_ids', 'product_id', 'employee_id.user_id.partner_id', 'quantity')
    # def _compute_total_amount_company(self):
    #     for expense in self:
    #         base_lines = [expense._convert_to_tax_base_line_dict(
    #             price_unit=expense.total_amount * expense.currency_rate,
    #             currency=expense.company_currency_id,
    #         )]
    #         taxes_totals = self.env['account.tax']._compute_taxes(base_lines)['totals'][expense.company_currency_id]
    #         expense.total_amount_company = taxes_totals['amount_untaxed'] + taxes_totals['amount_tax']
    #         expense.amount_tax_company = taxes_totals['amount_tax']

    @api.onchange('total_amount')
    def _inverse_total_amount(self):
        pass
        # for expense in self:
        #     expense.unit_amount = expense.total_amount_company / (expense.quantity or 1)

    @api.depends('product_id.standard_price')
    def _compute_product_has_cost(self):
        for expense in self:
            expense.product_has_cost = expense.product_id and (float_compare(expense.product_id.standard_price, 0.0, precision_digits=2) != 0)
            tax_ids = expense.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == expense.company_id)
            expense.product_has_tax = bool(tax_ids)
            # if not expense.product_has_cost and expense.state == 'draft':
            #     expense.unit_amount = expense.total_amount_company
            #     expense.quantity = 1

    @api.depends('product_id', 'attachment_number', 'currency_rate')
    def _compute_unit_amount(self):
        pass
        # for expense in self:
        #     if expense.state != 'draft':
        #         continue
        #     product_id = expense.product_id
        #     if product_id and expense.product_has_cost and not expense.attachment_number or (expense.attachment_number and not expense.unit_amount):
        #         expense.unit_amount = product_id.price_compute(
        #             'standard_price',
        #             uom=expense.product_uom_id,
        #             company=expense.company_id,
        #         )[product_id.id]
        #     else:  # Even if we don't add a product, the unit_amount is still used for the move.line balance computation
        #         currency_id = expense.company_currency_id or expense.currency_id
        #         expense.unit_amount = currency_id.round(expense.total_amount_company / (expense.quantity or 1))

    @api.depends('date', 'currency_id', 'company_currency_id', 'company_id')
    def _compute_currency_rate(self):
        date_today = fields.Date.context_today(self.env.user)
        for expense in self:
            target_currency = expense.currency_id or self.env.company.currency_id
            to_currency = expense.company_currency_id or expense.currency_id
            expense.currency_rate = expense.company_id and self.env['res.currency']._get_conversion_rate(
                from_currency=target_currency,
                to_currency=to_currency,
                company=expense.company_id,
                date=expense.date or date_today,
            )

    def _prepare_move_line_vals(self):
        self.ensure_one()
        account = self.account_id
        if not account:
            # We need to do this as the installation process may delete the original account and it doesn't recompute properly after.
            # This forces the default values if none is found
            if self.product_id:
                account = self.product_id.product_tmpl_id._get_product_accounts()['expense']
            else:
                account = self.env['ir.property']._get('property_account_expense_categ_id', 'product.category')

        return {
            'name': self.employee_id.name + ': ' + self.name.split('\n')[0][:64],
            'account_id': account.id,
            'quantity': self.quantity or 1,
            'price_unit': self.unit_amount,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom_id.id,
            'analytic_distribution': self.analytic_distribution,
            'expense_id': self.id,
            'partner_id': False if self.payment_mode == 'company_account' else self.employee_id.sudo().address_home_id.commercial_partner_id.id,
            'tax_ids': [Command.set(self.tax_ids.ids)],
        }

    @api.depends('employee_id', 'product_id', 'total_amount')
    def _compute_duplicate_expense_ids(self):
        self.duplicate_expense_ids = [(5, 0, 0)]

        expenses = self.filtered(lambda e: e.employee_id and e.product_id and e.total_amount)
        if expenses.ids:
            duplicates_query = """
              SELECT ARRAY_AGG(DISTINCT he.id)
                FROM hr_expense AS he
                JOIN hr_expense AS ex ON he.employee_id = ex.employee_id
                                     AND he.product_id = ex.product_id
                                     AND he.date = ex.date
                                     AND he.total_amount = ex.total_amount
                                     AND he.company_id = ex.company_id
                                     AND he.currency_id = ex.currency_id
                                     AND he.analytic_distribution = ex.analytic_distribution
               WHERE ex.id in %(expense_ids)s
               GROUP BY he.employee_id, he.product_id, he.date, he.total_amount, he.company_id, he.currency_id, he.analytic_distribution
              HAVING COUNT(he.id) > 1
            """
            self.env.cr.execute(duplicates_query, {
                'expense_ids': tuple(expenses.ids),
            })
            duplicates = [x[0] for x in self.env.cr.fetchall()]

            for ids in duplicates:
                exp = expenses.filtered(lambda e: e.id in ids)
                exp.duplicate_expense_ids = [(6, 0, ids)]
                expenses = expenses - exp
