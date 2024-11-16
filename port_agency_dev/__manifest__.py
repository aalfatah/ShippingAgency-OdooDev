{
    'name': 'Port Agency Management',
    'version': '16.0.1.0.0',
    'summary': 'Port Agency',
    'description': """
        Helps you to manage port agency.
        """,
    'category': 'Sales/Sales',
    'author': "Dev",
    'maintainer': 'Dev',
    'depends': [
        'base_dev', 'sale', 'sales_team'
    ],
    # 'external_dependencies': {
    #     'python': ['pandas'],
    # },
    'data': [
        'security/ir.model.access.csv',
        'views/port_agency_views.xml',
        'views/agency_vessel_views.xml',
        'views/agency_port_views.xml',
        'views/agency_cost_package_views.xml',
        'views/agency_cost_header_views.xml',
        'views/agency_cost_item_views.xml',
        'views/agency_cost_structure_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
# -- coding: utf-8 --
