# -*- coding: utf-8 -*-
# Copyright (C) 2020-2022 Artem Shurshilov <shurshilov.a@yandex.ru>
# License OPL-1.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "hr attendance face recognition",

    'summary': """
Face recognition check in / out
is a technology capable of identifying or verifying a person
from a digital image or a video frame from a video source""",

    'author': "EURO ODOO, Shurshilov Artem",
    'website': "https://eurodoo.com",
    "live_test_url": "https://eurodoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '15.3.2.3',
    "license": "OPL-1",
    'price': 72,
    'currency': 'EUR',
    'images': [
        'static/description/preview.gif',
        'static/description/face_control.png',
        'static/description/face_control.png',
        'static/description/face_control.png',
    ],

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'hr_attendance_base', 'web_image_webcam'],

    'assets': {
        'web.assets_backend': [
            'hr_attendance_face_recognition/static/src/css/toogle_button.css',
            'hr_attendance_face_recognition/static/src/js/lib/webcam.js',
            'hr_attendance_face_recognition/static/src/js/lib/face-api.min.js',
            'hr_attendance_face_recognition/static/src/js/widget_image_recognition.js',
            'hr_attendance_face_recognition/static/src/js/res_users_kanban_face_recognition.js',
            'hr_attendance_face_recognition/static/src/js/my_attendances_face_recognition.js',
            'hr_attendance_face_recognition/static/src/js/kiosk_mode_face_recognition.js',
        ],
        'web.assets_qweb': [
            'hr_attendance_face_recognition/static/src/xml/**/*.xml',
        ],
    },

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/assets.xml',
        'views/views.xml',
        'views/res_users.xml',
        'views/hr_employee.xml',
        'views/res_config_settings_views.xml',
    ],
    'qweb': [
        "static/src/xml/attendance.xml",
        "static/src/xml/kiosk.xml",
    ],

    "cloc_exclude": [
        "static/src/js/lib/**/*",  # exclude a single folder
    ]
}
