# -*- coding: utf-8 -*-
{
    'name': "Biometric Attendance Download",
    "author": "Global Solutions",
    "website": "https://globalsolutions.dev",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'hr', 'hr_attendance', ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'data/data2.xml',
        'views/hr_attendance.xml',
        'views/biometric_view.xml',
        'wizard/schedule_wizard.xml',
    ],
}
