# -*- coding: utf-8 -*-
{
    'name': "Gs HR Penalties & Awards",
    "author": "Global Solutions",
    "website": "https://globalsolutions.dev",
    'category': 'Human Resources/Employees',
    'version': '0.1',
    'depends': ['base', 'gs_hr_insurance', 'gs_hr_contract_allowance'],
    "images": [
        'static/description/icon.png'
    ],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/mail_template.xml',
        'wizard/send_by_email.xml',
        'views/penalties_awards_setting.xml',
        'views/penalties_awards.xml',
        'views/hr_employee_view.xml',
        'views/hr_payslip_view.xml',
        'data/data2.xml',

    ],
    'installable': True,
    'application': True,
}
