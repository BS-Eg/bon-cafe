# -*- coding: utf-8 -*-
{
    'name': "Gs Notification",
    "author": "Global Solutions",
    "website": "https://globalsolutions.dev",
    'category': 'Human Resources/Employees',
    'version': '0.1',
    'depends': ['base', 'mail', 'calendar', 'gs_employee', 'hr', 'gs_hr_contracts_management', 'hr_contract'],
    "images": [
        'static/description/icon.png'
    ],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'views/notification.xml',
        'views/alarm.xml',
        'views/notification_user.xml',
        'views/template.xml',
        'wizard/get_data.xml',
        'data/cron.xml',
    ],
    'assets': {
        'web.assets_qweb': [
            'gs_notification/static/src/xml/tree_header_extend.xml'
        ],
        'web.assets_backend': [
            '/gs_notification/static/src/core.css',
            '/gs_notification/static/src/js/tree_header_extend.js',
        ],
    },
    'installable': True,
    'application': True,
}
