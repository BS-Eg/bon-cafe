# -*- coding: utf-8 -*-
{
    'name': "Global Solutions Edit Employee",
    "author": "Global Solutions",
    "website": "https://globalsolutions.dev",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'hr', 'gs_hr_employee_updation', 'gs_hr_insurance'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/residence_profession.xml',
        'views/type_of_license.xml',
        'views/driving_license_restriction.xml',
        'views/evaluated_by.xml',
        'views/tasks.xml',
        'views/evaluated_by.xml',
        'views/kpi_table.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
