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
    "name": "Portal Payslip",
    "summary": """This module allows portal users to view their payslip in Odoo portal.""",
    "version": "15.0.0",
    "description": """
        This module allows portal users to view their payslip in Odoo portal.
    """,    
    "author": "CFIS",
    "maintainer": "CFIS",
    "license" :  "Other proprietary",
    "website": "https://www.cfis.store",
    "images": ["images/portal_payslip.png"],
    "category": "Attendances",
    "depends": [
        "base",
        "hr_payroll",
        "web",
        "portal"
    ],
    "data": [
        "security/ir.model.access.csv",
        "report/hr_payslip_template.xml",
        "report/hr_payslip_reports.xml",
        "views/templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
        ],
        "web.assets_backend": [
        ],
        "web.assets_qweb": [
        ],
    },
    "installable": True,
    "application": True,
    "price"                 :  55,
    "currency"              :  "EUR",
    "pre_init_hook"         :  "pre_init_check",
}
