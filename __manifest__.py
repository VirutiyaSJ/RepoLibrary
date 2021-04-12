# -*- coding: utf-8 -*-
{
    'name':        "LIBRARY Management",

    'summary':
                   """
                   Library Management
                   """,

    'description': """
        Manage a LIBRARY: customers, books, etc.... 
    """,

    'author':      "Odoo",
    'website':     "http://www.odoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category':    'Library',
    'version':     '0.6',

    # any module necessary for this one to work correctly
    'depends':     ['base','product','website'],

    # always loaded
    'data':        [
        "security/ir.model.access.csv",
        "views/book_views.xml",
        "views/partner_views.xml",
        "views/rental_views.xml",
        "views/author_views.xml",
        "views/price_views.xml",
        "views/payment_views.xml",
        "views/menu_views.xml",
        "views/templates.xml",  
        "wizard/select_book_views.xml",
        "report/reports.xml",
        "data/cron.xml",
        "data/mail.xml",
        "data/library_data.xml",
	'views/website_form.xml',
    ],
    # only loaded in demonstration mode
    'demo':        [],
    'license': 'AGPL-3',
}
