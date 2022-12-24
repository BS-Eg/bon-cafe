{
    'name': 'POS Loyalty Customer',
    'version': '14.1.0.0',
    'author': 'Khalid BENTALEB',
    'summary': 'POS Loyalty by customer',
    'description': """
        this module allows to manage loyalty by customer
    """,
    'website': 'https://globalsolutions.dev/',
    'depends': ['pos_loyalty'],
    'category': 'Tools',
    'data': [
        'views/assets.xml',
        'views/res_partner_views.xml',
        'views/loyalty_views.xml'
    ],
    'assets': {
        'point_of_sale.assets': [
            'gs_pos_loyalty/static/src/js/db.js',
            'gs_pos_loyalty/static/src/js/loyalty.js',
            'gs_pos_loyalty/static/src/js/client.js',
            'gs_pos_loyalty/static/src/js/RewardButton.js',
            'gs_pos_loyalty/static/src/js/PointsCounter.js',
            'gs_pos_loyalty/static/src/js/AbstractReceiptScreen.js',
        ],
        'web.assets_qweb': [
            'gs_pos_loyalty/static/src/xml/**/*',
            'gs_pos_loyalty/static/src/xml/loyalty.xml',
            'gs_pos_loyalty/static/src/xml/numberpopup.xml',
            'gs_pos_loyalty/static/src/xml/ClientListScreen.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
}
