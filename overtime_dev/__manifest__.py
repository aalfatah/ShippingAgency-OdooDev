{
    'name': 'Overtime Dev',
    'version': '16.0.1.0.0',
    'summary': 'Manage Employee Overtime',
    'description': """
        Helps you to manage Employee Overtime Dev.
        """,
    'category': 'Generic Modules/Human Resources',
    'author': "Dev Team",
    'company': 'Dev',
    'maintainer': 'Dev',
    'depends': [
        'ohrms_overtime',
        'hr_payroll_dev',
        'hr_contract',
        'hr_payroll_cancel',
        'hr_public_holiday_dev',
        # 'hr_attendance_dev',
        # 'hr_employee_shift'
    ],
    'external_dependencies': {
        'python': ['pandas'],
    },
    'data': [
        # 'data/data.xml',
        'security/overtime_security.xml',
        'security/ir.model.access.csv',
        'views/overtime_type.xml',
        'views/overtime_request.xml',
        # 'views/overtime_limit.xml',
        # 'views/calendar_leave_views.xml',
        # 'views/payroll_assign_other_input_views.xml',
        'views/res_config_settings_views.xml',
        'wizard/hr_overtime_mass_confirm.xml',
    ],
    'demo': [],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
