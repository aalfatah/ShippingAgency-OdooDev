# -- coding: utf-8 --
{
    'name': 'Purchase Dev',
    'version': '16.0.1.0.0',
    'category': 'Inventory/Purchase',
    'summary': 'Purchase',
    'description': """
        Helps you to enhance purchase module.
        """,
    'author': "Dev",
    'maintainer': 'Dev',
    'depends': [
        'purchase', 'purchase_requisition'
    ],
    'data': [
        'views/purchase_views.xml',
        'reports/purchase_order_templates.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
