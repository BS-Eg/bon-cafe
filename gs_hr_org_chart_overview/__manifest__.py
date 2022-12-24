# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "GS HR Org Chart Overview",
    "version": "15.0.1.0.0",
    "category": "Human Resources",
    "author": "Global Solutions",
    "website": "https://globalsolutions.dev",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "Organizational Chart Overview",
    "depends": ["hr"],
    "data": ["views/hr_org_chart_overview_templates.xml", "views/hr_views.xml"],
    'css': ['static/src/lib/orgchart/jquery.orgchart.css'],

    'assets': {
        'web.assets_qweb': [
            'gs_hr_org_chart_overview/static/src/xml/hr_org_chart_overview.xml'
        ],
        'web.assets_backend': [
            "/gs_hr_org_chart_overview/static/src/js/hr_org_chart_overview.js",
            "/gs_hr_org_chart_overview/static/src/lib/orgchart/html2canvas.min.js",
            "/gs_hr_org_chart_overview/static/src/lib/orgchart/jspdf.min.js",
            "/gs_hr_org_chart_overview/static/src/lib/orgchart/jquery.orgchart.js",
            "/gs_hr_org_chart_overview/static/src/scss/hr_org_chart_style.scss",
        ],
    },
}
