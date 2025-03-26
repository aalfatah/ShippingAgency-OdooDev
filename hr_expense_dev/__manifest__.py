{
    "name": "HR Expense DEV",
    "summary": "HR Expense DEV",
    "category": "HR",
    "author": "DEV Team",
    "license": "",
    "installable": True,
    "maintainers": ["DEV"],
    "depends": [
        "hr_expense",
        'hr_expense_advance_clearing',
        'hr_dev'
    ],
    "data": [
        "views/hr_expense_views.xml",
        "reports/hr_expense_report.xml",
    ],
    "sequence": 100,
    "license": "LGPL-3",
}
