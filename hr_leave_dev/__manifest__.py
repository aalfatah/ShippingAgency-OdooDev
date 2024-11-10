{
    "name": "HR Leave DEV",
    "summary": "HR Leave DEV",
    "category": "HR",
    "author": "DEV Team",
    "license": "",
    "installable": True,
    "maintainers": ["DEV"],
    "depends": [
        "hr",
        "hr_holidays",
    ],
    "data": [
        # "security/ir.model.access.csv",
        # "views/hr_leave_type_views.xml",
        "views/hr_leave_views.xml",
        "views/hr_leave_allocation_views.xml",
        # "views/hr_employee_views.xml",
        # "data/hr_leave_sch.xml",
    ],
    "sequence": 1,
    "license": "LGPL-3",
}
