# -*- coding: utf-8 -*-
{
    'name' : 'Dynamic Financial Reports Dev v16',
    'sequence': 15,
    'category': 'Accounting/Accounting',
    'author': 'Dev Team',
    'depends': ['account'],
    'data': [
             # 'security/ir.model.access.csv',
             # 'data/data_financial_report.xml',
             #
             # 'views/views.xml',
             # 'views/general_ledger_view.xml',
             # 'views/res_config_settings_view.xml',
             # 'views/partner_ageing_view.xml',
             # 'views/financial_report_view.xml',
             # 'views/partner_ledger_view.xml',
             # 'views/trial_balance_view.xml',
             #
             # 'wizard/partner_ageing_view.xml',
             # 'wizard/financial_report_view.xml',
             # 'wizard/general_ledger_view.xml',
             # 'wizard/partner_ledger_view.xml',
             # 'wizard/trial_balance_view.xml',
             
             ],
    'assets' : {
        'web.assets_backend': [
            'account_dynamic_reports_dev/static/src/scss/dynamic_common_style.scss',
            'account_dynamic_reports_dev/static/src/js/select2.full.min.js',
            'account_dynamic_reports_dev/static/src/js/gl.js',
            'account_dynamic_reports_dev/static/src/js/fr.js',
            'account_dynamic_reports_dev/static/src/js/pa.js',
            'account_dynamic_reports_dev/static/src/xml/**/*',
            'account_dynamic_reports_dev/static/src/js/pl.js',
            'account_dynamic_reports_dev/static/src/js/tb.js',
        ],
    },
    'qweb': ['static/src/xml/view.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
