#    Author: Warlock Technologies Pvt Ltd.(<https://www.warlocktechnologies.com/>)
###################################################################################
{
    'name': 'POS COMBO',
    'version': '15.0.0.1',
    'category': 'point_of_sale',
    'summary': 'pos combo',
    'description': '''
        pos combo product
    ''',
    'author': 'Warlock Technologies Pvt Ltd.',
    'website': 'http://warlocktechnologies.com',
    'support': 'support@warlocktechnologies.com',
    'depends': ['point_of_sale'],
    "data": [
        'security/ir.model.access.csv',
        'views/views.xml',
        ],
    "price": 100,
    "currency": "USD",
    'assets': {
        'point_of_sale.assets': [
            'wt_pos_combo/static/src/css/pos_combo.css',
            'wt_pos_combo/static/src/js/db.js',
            'wt_pos_combo/static/src/js/models.js',
            'wt_pos_combo/static/src/js/popup/PosComboConfigurePopup.js',
            'wt_pos_combo/static/src/js/screens/screens.js',
        ],
        'web.assets_qweb': [
            'wt_pos_combo/static/src/xml/pos_combo.xml',
        ],
    },
    'images': ['static/images/screen_image.png'],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
}
