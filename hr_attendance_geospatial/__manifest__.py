# -*- coding: utf-8 -*-
# Copyright (C) 2019 Artem Shurshilov <shurshilov.a@yandex.ru>
# License OPL-1.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "hr attendance  professional policy geospatial address mechanism",

    'summary': """
        Module allows you to automatically check whether an employee
        is in a given geofence (store or office) with GPS coordinates
        accuracy from html5 standard (1 meter at best)""",

    'author': "EURO ODOO, Shurshilov Artem",
    'website': "https://eurodoo.com",
    "live_test_url": "https://eurodoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '15.0.0.2',
    "license": "OPL-1",
    'price': 100,
    'currency': 'EUR',
    'images': [
        'static/description/preview.gif',
    ],

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'hr_attendance_base', 'hr_attendance_geo_html'],
    "external_dependencies": {"python": ["pyproj", "shapely"]},
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/hr_attendance_security.xml',
        'views/views.xml',
        'views/res_config_settings_views.xml',
    ],
    # 'qweb': [
    #     "static/src/xml/attendance.xml",
    # ],

    'assets': {
        'web.assets_backend': [
            'hr_attendance_geospatial/static/src/js/attendances_geospatial.js',
        ],
        'web.assets_qweb': [
            'hr_attendance_geospatial/static/src/**/*.xml',
        ],
    },
}
