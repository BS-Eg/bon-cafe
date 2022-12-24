# -*- coding: utf-8 -*-
{
    'name': "Gs HR EOS",
    "author": "Global Solutions",
    "website": "https://globalsolutions.dev",
    'category': 'Human Resources/Employees',
    'version': '0.1',
    'depends': ['base', 'gs_hr_insurance', 'gs_hr_contract_allowance', 'hr_payroll', 'account_accountant'],
    "images": [
        'static/description/icon.png'
    ],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'demo/demo.xml',
        'views/end_reason.xml',
        'views/eos.xml',
        'views/res_config_settings.xml',
        'views/eos_monthly.xml',
        'data/cron_jobs.xml',

    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
}
