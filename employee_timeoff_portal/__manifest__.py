# -*- coding: utf-8 -*-
#################################################################################
# Author      : CodersFort (<https://codersfort.com/>)
# Copyright(c): 2017-Present CodersFort.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://codersfort.com/>
#################################################################################
{
    "name": "Employee Time Off Portal (Employee Leave Portal)",
    "summary": "This module is to allow the Portal users can manage Time Off request from Portal User Account.",
    "version": "15.0.1",
    "description": """This module is to allow the Portal users can manage Time Off request from Portal User Account.""",    
    "author": "CodersFort",
    "maintainer": "Ananthu Krishna",
    "license" :  "Other proprietary",
    "website": "http://www.codersfort.com",
    "images": ["images/employee_timeoff_portal.png"],
    "category": "Portal",
    "depends": [
        "website",
        "portal",
        "hr",
        "hr_holidays",
    ],
    "data": [
    	'security/ir.model.access.csv',
        "views/hr_employee_views.xml",
        "views/hr_leave_portal_templates.xml",
        
    ],
    "assets": {
        "web.assets_frontend": [
            "/employee_timeoff_portal/static/src/js/timeoff_portal.js",
            "/employee_timeoff_portal/static/src/css/style.css",
        ]
    },
    "qweb": [],
    "installable": True,
    "application": True,
    "price"                :  85,
    "currency"             :  "EUR",
    "pre_init_hook"        :  "pre_init_check",   
}
