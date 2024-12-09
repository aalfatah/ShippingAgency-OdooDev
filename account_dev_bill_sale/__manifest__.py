# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Vendor Bill Relation Sales Order',
    'version': '16.0',
    'summary': 'Vendor Bill',
    'sequence': 10,
    'description': """
Invoicing & Payments
====================
Modify journal view show secure_sequence_id field
    """,
    'category': 'Accounting/Accounting',
    'depends': ['account', 'sale'],
    'data': [
        'views/account_move_views.xml',
        'reports/payment_request.xml',
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
