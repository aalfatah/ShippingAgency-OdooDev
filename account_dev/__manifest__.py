# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Invoicing Dev',
    'version': '16.0',
    'summary': 'Invoices & Payments',
    'sequence': 10,
    'description': """
Invoicing & Payments
====================
Modify journal view show secure_sequence_id field
    """,
    'category': 'Accounting/Accounting',
    'depends': ['account', 'account_menu_invoice_refund', 'partner_manual_rank'],
    'data': [
        'views/account_move_views.xml',
        'views/account_payment_view.xml',
        'reports/print_payment_voucher.xml',
        'reports/report_account_move.xml',
        'reports/report_invoice.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
