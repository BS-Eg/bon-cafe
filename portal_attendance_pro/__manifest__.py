# -*- coding: utf-8 -*-
#################################################################################
# Author      : CFIS (<https://www.cfis.store/>)
# Copyright(c): 2017-Present CFIS.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://www.cfis.store/>
#################################################################################

{
    "name": "Portal Employee Attendance | Portal Attendance | Attendance Portal | Geolocation | Geofence | Attendance Photo",
    "summary": """This module allows portal users to view their attendance as well as mark their attendance in Odoo. 
        This module additionally provides the benefits of geolocation, geofencing, and photo capturing
        while portal users use Check in and Check out options.""",
    "version": "15.0.1",
    "description": """
        This module allows portal users to view their attendance as well as mark their attendance in Odoo. 
        This module additionally provides the benefits of geolocation, geofencing, and photo capturing 
        while portal users use Check in and Check out options.
    """,    
    "author": "CFIS",
    "maintainer": "CFIS",
    "license" :  "Other proprietary",
    "website": "https://www.cfis.store",
    "images": ["images/portal_attendance_pro.png"],
    "category": "Attendances",
    "depends": [
        "base",
        "hr_attendance",
        "website",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/geolocation_data.xml",
        "views/res_config_settings.xml",
        "views/hr_employee_views.xml",
        "views/hr_attendance_templates.xml",
        "views/hr_attendance_view.xml",
        "views/hr_attendance_geofence.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "/portal_attendance_pro/static/src/lib/sweetalert2/sweetalert2.css",
            "/portal_attendance_pro/static/src/lib/sweetalert2/sweetalert2.js",
            "/portal_attendance_pro/static/src/js/portal_attendance.js",
            "/portal_attendance_pro/static/src/css/style.css",
            "/portal_attendance_pro/static/src/css/olmap.css",
        ],
        "web.assets_backend": [
            "/portal_attendance_pro/static/src/lib/sweetalert2/sweetalert2.css",
            "/portal_attendance_pro/static/src/lib/sweetalert2/sweetalert2.js",
            "/portal_attendance_pro/static/src/css/olmap.css",
            "/portal_attendance_pro/static/src/css/style_backend.css",
            "/portal_attendance_pro/static/src/js/geofence_drawing.js",
            "/portal_attendance_pro/static/src/js/geofence_model.js",
            "/portal_attendance_pro/static/src/js/geofence_controller.js",
            "/portal_attendance_pro/static/src/js/geofence_renderer.js",
            "/portal_attendance_pro/static/src/js/geofence_view.js",
            "/portal_attendance_pro/static/src/js/geofence_common.js",
            "/portal_attendance_pro/static/src/js/my_attendances.js",
        ],
        "web.assets_qweb": [
            "/portal_attendance_pro/static/src/xml/*.xml"
        ],
    },
    "installable": True,
    "application": True,
    "price"                 :  350,
    "currency"              :  "EUR",
    "pre_init_hook"         :  "pre_init_check",
}
