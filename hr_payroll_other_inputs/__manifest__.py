# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Other payroll input",
    "version": "16.0.0.0.0",
    "author": "JUVENTUD PRODUCTIVA VENEZOLANA",
    "category": "Human Resources",
    "website" : "https://www.youtube.com/channel/UCTj66IUz5M-QV15Mtbx_7yg",
    "description": "This module allows us to add assignments or special discounts to our payroll by integrating the other inputs section.",
    "license": "AGPL-3",
    "depends": ['base','hr','hr_payroll_community','report_xlsx'],
    "data": [
        'sequence/sequence.xml',
        'report/report_excel.xml',
        'views/payroll_other_inputs_view.xml',
        'wizard/payroll_assign_other_input_views.xml',
        'security/ir.model.access.csv',
    ],
    'images': ['static/images/input_screenshot.png'],
    "active": True,
    "installable": True,
    'currency': 'EUR',
    'price': 39.00,
}
