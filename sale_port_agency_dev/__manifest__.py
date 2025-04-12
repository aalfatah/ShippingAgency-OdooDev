{
    "name": "Sale Order Dev",
    "version": "16.0.0.0.0",
    "category": "Sales Management",
    "author": "Dev Team,",
    "license": "LGPL-3",
    "depends": ["sale", "sale_management", "sale_dev", "port_agency_dev", "hr_expense", "sale_project"],
    "data": [
        "security/ir.model.access.csv",
        "security/port_agency_security.xml",
        "views/sale_order_view.xml",
        "views/sale_cost_structure_views.xml",
        "views/hr_expense_view.xml",
        "views/account_move_views.xml",
        "views/project_views.xml",
        "views/project_cost_structure_views.xml",
        "wizard/sync_rate_card_wizard_view.xml",
        # "reports/sale_order_quotation.xml",
        # "reports/sale_order_bast.xml",
    ],
    # 'assets': {
    #    'web.assets_backend': [
    #        'sale_port_agency_dev/static/src/js/cost_structure_extend.js',
    #        'sale_port_agency_dev/static/src/xml/cost_structure_sync_button.xml',
    #    ]
    # },
    "installable": True,
}
