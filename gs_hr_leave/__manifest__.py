# -*- coding: utf-8 -*-
{
    'name': "GS HR Leaves",
    'summary': """ Time Off""",
    'description': """  Time Off """,
    "author": "Global Solutions",
    "website": "https://globalsolutions.dev",
    'category': 'Human Resources/Employees',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'hr_holidays'],
    # always loaded
    'data': [
        'data/cron.xml',
        'data/data2.xml',
        'views/hr_employee_inherit.xml',
        'views/leave_inherit.xml',
        'views/contract_inherit.xml',
        'views/allocation_inherit.xml',
    ],
    # only loaded in demonstration mode
    'installable': True,
    'application': True,
}
