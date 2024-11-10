{
    "name": "Payroll Dev",
    "summary": "Payroll Dev",
    "category": "HR",
    "author": "Dev Team",
    'license': 'LGPL-3',
    "installable": True,
    "maintainers": ["Dev"],
    "depends": [
        "hr_payroll_dev","hr_dev"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_payroll_ter_views.xml",
        "views/hr_payroll_ptkp_views.xml",
        "views/hr_payslip_views.xml",
    ],
    "sequence": 1,
}
