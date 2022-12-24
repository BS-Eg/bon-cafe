# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name" : "Portal Timesheet",
    "author" : "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Portal",
    "summary": "Do you want to manage timesheet at the portal?",
    "description": """
Do you want to manage timesheet at the portal? Using this module you can create timesheet from the website portal. You can edit or delete timesheet using "Action". You can sort by timesheet by newest and name. We have provided filter timesheet option so easy to filter timesheet by last month, last week, last year, this month, this quarter, today, this week & this year. You can easily group by timesheet activities by their assigned Projects. Using a search bar you can search timesheet easily.

 Portal Timesheet Odoo
 Create Timesheet On Website Module, Make Portal Timesheet, Edit Timesheet On Portal, Delete Timesheet On Web, Filter Portal Timesheet, Group By Portal Timesheet, Portal Timesheet, Website Timesheet, Timesheet Portal, Timesheet Website Odoo
 Create Timesheet On Website Module, Make Portal Timesheet, Edit Timesheet Portal, Delete Timesheet On Web, Filter Portal Timesheet, Group By Portal Timesheet, Portal Timesheet, Website Timesheet, Timesheet Portal, Timesheet Website Odoo
                    """,
    "version":"15.0.1",
    "depends" : ["hr_timesheet","portal"],
    "application" : True,
    "data" : [
            'security/ir.model.access.csv',
            'views/sh_portal_timesheet_view.xml',
            ],
    'assets': {
    'web.assets_frontend': [
        'sh_portal_timesheet/static/src/js/portal.js',
    ],
    },
    "images": ["static/description/background.png", ],
    "live_test_url": "https://youtu.be/X_pBrQUDFOk",
    "auto_install":False,
    "installable" : True,
    "price": 100,
    "currency": "EUR"
}