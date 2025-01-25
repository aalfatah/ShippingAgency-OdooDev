# -*- coding: utf-8 -*-
{
    'name' : 'All in one Dynamic Financial Reports v16 Dev',
    'version' : '16.0.1',
    'summary': "General Ledger Trial Balance Ageing Balance Sheet Profit and Loss Cash Flow Dynamic",
    'sequence': 15,
    'description': """
                    Odoo 16 Full Accouning, Odoo 16 All in one Accouning, PDF Reports, XLSX Reports,
                    Dynamic View, Drill down, Clickable, Pdf and Xlsx package, Odoo 16 Accounting,
                    Full Account Reports, Complete Accounting Reports, Financial Report for Odoo 13,
                    Financial Reports, Excel reports, Financial Reports in Excel, Ageing Report,
                    General Ledger, Partner Ledger, Trial Balance, Balance Sheet, Profit and Loss,
                    Financial Report Kit, Cash Flow Statements, Cash Flow Report, Cash flow, Dynamic reports,
                    Dynamic accounting, Dynamic financial, Community, CE
                    """,
    'category': 'Accounting/Accounting',
    'author': 'Dev Smits',
    'maintainer': 'Dev Smits',
    'website': '',
    'depends': ['account_dynamic_reports'],
    'data': [
             'wizard/partner_ageing_view.xml',
             'wizard/partner_ledger_view.xml',
             'views/partner_ledger_view.xml',
             ],
    'license': 'OPL-1',
    'installable': True,
    'application': False,
    'auto_install': False,
}
