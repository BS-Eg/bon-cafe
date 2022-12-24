# -*- coding: utf-8 -*-
{
    'name': "GS HR Contract Renew",
    "author": "Global Solutions",
    "website": "https://globalsolutions.dev",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'hr_contract'],

    # always loaded
    'data': [
        'data/cron.xml',
        'data/ir_sequence.xml',
        'security/ir.model.access.csv',
        'wizard/set_renew.xml',
        'views/hr_contract_inherit.xml',
    ],
}
