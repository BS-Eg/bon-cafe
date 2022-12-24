# Part of Warlock. See LICENSE file for full copyright and licensing details.
{
    'name': 'WT Portal Attendances',
    'version': '15.0.1',
    'category': 'Human Resources/Attendances',
    'sequence': 365,
    'summary': 'WT Portal Attemdances',
    'description': """WT Portal Attemdances""",
    'depends': ['hr_attendance', 'hr_holidays', 'hr_payroll', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/template.xml',
        'views/portal_attendance.xml',
        'wizard/portal_wizard_views.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'https://cdn.jsdelivr.net/npm/daterangepicker/daterangepicker.min.js',
            'https://cdn.jsdelivr.net/npm/daterangepicker/daterangepicker.css',
            'wt_portal_attendances/static/src/scss/attendance.scss',
            'wt_portal_attendances/static/src/js/attendance.js'
        ],
        'web.assets_qweb': [
            'wt_portal_attendances/static/src/xml/attendance.xml',
        ],
    },
    'application': True,
    'license': 'LGPL-3',
}
