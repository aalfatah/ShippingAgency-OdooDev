{
	"name": "E-Faktur Management for Indonesia Tax",
	"version": "1.0", 
	"depends": [
		"account",
		"stock",
		"efaktur_location_dev",
	],
	'images': ['static/description/images/main_screenshot.png'],
	"author": "Dev Team",
    'category': 'Accounting',
    'price':'30',
    'currency': 'USD',
	"category": "Accounting",
	"summary": "Manage, Export and Import, Tag Invoice with E-Faktur, the online tax management system for Indonesian companies",
	"description": """\

Manage
======================================================================

* Pengelolaan eFaktur Pajak Indonesia
* created menu:
* created object
* created views
* logic:

""",
	"data": [
		"security/ir.model.access.csv",
		"wizard/generate.xml",
		"wizard/product.xml",
		"wizard/partner.xml",
		"wizard/pk.xml",
		"wizard/auto.xml",
		"wizard/pm.xml",

		"view/product.xml",
		"view/efaktur.xml",
		"view/partner.xml",
		"view/account_move_views.xml",
		"view/invoice_supplier.xml",

	],
	"application": True,
	"installable": True,
	"auto_install": False,
	"license": "LGPL-3",
}