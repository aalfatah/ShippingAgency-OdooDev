{
	"name": "Data Kelurahan, Kecamatan, Propinsi Indonesia",
	"version": "1.2",
	"depends": [
		"base",
		"sales_team",
		"sale_management",
		"account"
	],
	"author": "Dev Team",
	"category": "Sales",
	"description": """\

this module provide kecamatan, kelurahan, and state data for indonesian

""",
	"data": [
		"security/account_security.xml",
		"security/ir.model.access.csv",
		#"data/res.country.state.csv",
		"data/efaktur.kota.csv",
		"data/efaktur.kecamatan.csv",
		"data/efaktur.kelurahan.csv", # long loading
		"view/menu_efaktur.xml",
		"view/kelurahan.xml",
		"view/kecamatan.xml",
		"view/kota.xml",
		"view/partner.xml",
	],
	"installable": True,
	"auto_install": False,
    "application": True,
    "license": "AGPL-3",
}

