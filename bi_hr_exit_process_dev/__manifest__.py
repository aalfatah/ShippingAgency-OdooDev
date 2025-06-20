{
    "name": "Termination",
    "summary": "Termination Dev",
    "category": "HR",
    "author": "Dev Team",
    "license": "",
    "installable": True,
    "maintainers": ["Dev"],
    "depends": [
        "bi_hr_exit_process",
        "base_dev",
        "hr_dev",
        "hr_payroll_community",
    ],
    "data": [
        'data/sequence.xml',
        'data/hr_exit_sch.xml',
        # 'views/resignation_view.xml',
        'views/check_list_views.xml',
        'views/views_request_exit.xml',
        'views/hr_employee.xml',
        'views/hr_payslip_view.xml',
        'report/report_views.xml',
        'report/report_experience.xml',
        'security/ir.model.access.csv',
    ],
    "sequence": 99,
    "license": "LGPL-3",
}
