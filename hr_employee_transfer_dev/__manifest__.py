{
    "name": "HR Employee Transfer",
    "summary": "HR Employee Transfer Dev",
    "category": "HR",
    "author": "Dev Team",
    "license": "",
    "installable": True,
    "maintainers": ["Dev"],
    "depends": [
        "hr",
        "hr_employee_transfer",
    ],
    "data": [
        "sequence/sequence.xml",
        'security/ir.model.access.csv',
        'data/transfer_data.xml',
        "views/employee_transfer_views.xml",
        "views/hr_employee_views.xml",
        # "views/employee_tax_status_views.xml",
        "report/transfer_report.xml",
    ],
    "sequence": 2,
    "license": "AGPL-3",
}
