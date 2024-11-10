{
    'name': 'Public Holiday DEV',
    'version': '16.0.0.0.0',
    'summary': 'Manage Public Holiday',
    'description': """
        Helps you to manage public holiday.
        """,
    'category': 'Human Resources',
    'author': "DEV Team",
    'company': 'DEV',
    'maintainer': 'DEV',
    'depends': [
        'hr_holidays',
    ],
    'external_dependencies': {
        'python': ['pandas'],
    },
    'data': [
        'views/calendar_leave_views.xml',
    ],
    'demo': [],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
