# -*- coding: utf-8 -*-
{
    'name': "CDS Aramex Delivery Integrations",
    'summary': """
    """,
    'description': """
    """,
    'author': "CDS Solutions SRL,Ramadan Khalil",
    'website': "www.cdsegypt.com",
    'contributors': [
        'Ramadan Khalil <rkhalil1990@gmail.com>',
    ],

    'price': 170,
    'currency': 'EUR',
    'version': '14.0.1',
    'images': ['static/description/images/aramex_banner.jpg'],
    'depends': ['delivery','base_address_city','stock'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/city_data.xml',
        'data/ir_cron.xml',
        'views/delivery_aramex_view.xml',
        'views/res_config_settings_views.xml',
        'views/stock_picking_view.xml'
    ],
    'license': 'OPL-1',
}