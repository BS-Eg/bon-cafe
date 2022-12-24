# -*- coding: utf-8 -*-
# Copyright (C) 2019 Artem Shurshilov <shurshilov.a@yandex.ru>
# License OPL-1.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "hr attendance professional policy geolocation via html5 geolocate",

    'summary': " \
Module provides saves the geolocation of the geo-coordinates of \
the employee / user from the device on which it works displays \
them on the openstreet map and also allows you to view the \
geo-location of the employee in google maps geocoodrs employee \
employees geocoodrs coords employee geolocation employee geo employee \
geolocation users geolocation user geo geotracking \
",

    'author': "EURO ODOO, Shurshilov Artem",
    'website': "https://eurodoo.com",
    "live_test_url": "https://eurodoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '14.2.0.2',
    "license": "OPL-1",
    'price': 90,
    'currency': 'EUR',
    'images':[
        'static/description/Attendance_geo.png',
        'static/description/Attendance_geo.png',
        'static/description/Attendance_geo.png',
        'static/description/Attendance_geo.png',
    ],

    # any module necessary for this one to work correctly
    'depends': ['base','web','hr_attendance_base'],

    # always loaded
    'data': [
        'views/res_config_settings_views.xml',
        'views/views.xml',
    ],

    # 'qweb': [
    #     "static/src/xml/attendance.xml",
    # ],
    'assets': {
        'web.assets_backend': [
            'hr_attendance_geo_html/static/src/css/leaflet.css',
            'hr_attendance_geo_html/static/src/css/leaflet.fullscreen.css',
            'hr_attendance_geo_html/static/src/js/lib/leaflet.js',
            'hr_attendance_geo_html/static/src/js/lib/leaflet-geoip.js',
            'hr_attendance_geo_html/static/src/js/lib/leaflet.fullscreen.js',
            'hr_attendance_geo_html/static/src/css/geo.css',
            'hr_attendance_geo_html/static/src/js/geo_html_attendance.js'
        ],
        'web.assets_qweb': [
            'hr_attendance_geo_html/static/src/**/*.xml',
        ],
    },



}
