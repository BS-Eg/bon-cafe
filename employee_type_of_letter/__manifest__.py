# -*- coding: utf-8 -*-
# module template
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Type Of Letter',
    'version': '15.0',
    'author': "Global Solution",
    'depends': ['base','hr' ],
    'data': [
           'security/ir.model.access.csv',
           'security/security.xml',
             'views/letter_type.xml',
             'views/type_letter_template.xml',
            'report/reports.xml',
            'report/letter_report.xml',

             ],
    'installable': True,
    'application': True,
}
