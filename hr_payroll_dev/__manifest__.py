{
    "name": "PAYROLL Dev",
    "summary": "PAYROLL Dev",
    "category": "HR",
    "author": "Dev Team",
    "license": "",
    "installable": True,
    "maintainers": ["Dev"],
    "depends": [
        "hr","hr_payroll_community","hr_payroll_account_batch"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_payroll_ptkp_views.xml",
        "views/hr_payroll_pkp_views.xml",
        "views/hr_payroll_bpjs_views.xml",
        "views/hr_payslip_views.xml",
        "views/hr_payslip_run_views.xml",
        "views/hr_salary_rule_views.xml",
        "views/hr_employee_views.xml",
        "views/res_partner_views.xml",
        "views/hr_contract_views.xml",
        # "report/hr_payroll_report.xml",
        # "report/report_payslip_templates.xml",
    ],
    "sequence": 1,
    "license": "LGPL-3",
}
