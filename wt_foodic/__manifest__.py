# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    "name": "wt_foodic",
    "version": "14.0.0.1",
    "category": "Sales",
    "summary": "sync data from foodics to odoo.",
    "description": """
        with this application user able to sync branches, payment methods, categories, products and orders from foodics to odoo.
        from date and to date functionality
    """,
    "author": "Krishna Patel/Warlock Technologies Pvt Ltd.",
    "website": "http://warlocktechnologies.com",
    "support": "info@warlocktechnologies.com",
    "depends": ["product", "point_of_sale", "account"],
    "data": [
        'data/demo_data.xml',
        'data/cron.xml',
        'security/ir.model.access.csv',
        'wizard/message_view.xml',
        'views/connector_view.xml',
        'views/branches_view.xml',
        'views/payment_methods_view.xml',
        'views/categories_view.xml',
        'views/pos_orders_view.xml'
    ],
    "application": True,
    "installable": True,
    "auto_install": False,
    "image": ['static/image/screen_image.png'],
    "license": "OPL-1",
}


