# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Approval",
    "author": "DEV Team",
    "version": "16.0.1.0.0",
    "category": "Accounting",
    "website": "https://dev.com",
    "depends": ['account'],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/account_move_views.xml",
        "views/account_move_approval_views.xml",
        # "views/account_payment_views.xml",
        # "views/approval_title_view.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
}
