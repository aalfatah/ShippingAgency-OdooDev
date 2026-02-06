{
    'name': 'Custom Analytic Items Fields',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Menambahkan periode aktivitas ke Analytic Items',
    'author': 'Your Name',
    'depends': ['analytic', 'account','account_dev_bill_sale'],
    'data': [
        'views/analytic_line_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}