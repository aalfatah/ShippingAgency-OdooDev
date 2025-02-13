{
    "name": "Sale Order Dev",
    "version": "16.0.0.0.0",
    "category": "Sales Management",
    "author": "Dev Team,",
    "license": "LGPL-3",
    "depends": ["sale", "sale_management", "sale_dev", "port_agency_dev", "hr_expense"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_view.xml",
        "views/sale_cost_structure_views.xml",
        "views/hr_expense_view.xml",
        "views/account_move_views.xml",
        # "reports/sale_order_quotation.xml",
        # "reports/sale_order_bast.xml",
    ],
    "installable": True,
}
