{
    "name": "Employee Travel Expense Dev",
    "summary": "bi employee travel dev",
    "category": "HR",
    "author": "DEV Team",
    'license': 'LGPL-3',
    "installable": True,
    "maintainers": ["DEV"],
    "depends": [
        "bi_employee_travel", "hr_expense", "base_dev"
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "data/reminder.xml",
        # "data/advance_product.xml",
        "views/hr_expense_views.xml",
        "views/travel_type_views.xml",
        "views/travel_request_views.xml",
        "views/res_config_settings_views.xml",
        'report/employee_stpd_report.xml',
        'report/report_views.xml',
    ],
    "sequence": 1,
}
