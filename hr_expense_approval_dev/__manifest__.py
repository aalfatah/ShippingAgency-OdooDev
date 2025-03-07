# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Expense Approval",
    "author": "Dev Team",
    "version": "16.0.0.0.0",
    "category": "HR",
    "website": "https://smits.com",
    "depends": ["hr_expense", "account_approval_dev"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/expense_approval_views.xml",
        "views/expense_sheet_views.xml",
        # "reports/hr_expense_report.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
}
