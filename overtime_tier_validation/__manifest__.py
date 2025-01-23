# Copyright 2019-2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Overtime Tier Validation",
    "summary": "Extends the functionality of Overtimes to "
    "support a tier validation process.",
    "version": "16.0.0.0.0",
    "category": "Generic Modules/Human Resources",
    "website": "https://smits.com",
    "author": "Dev Teams",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["overtime_dev", "base_tier_validation"],
    "data": [
        'security/ir.model.access.csv',
        "data/overtime_tier_definition.xml",
        "views/overtime_request_view.xml",
        "wizard/hr_overtime_approval.xml",
    ],
}
