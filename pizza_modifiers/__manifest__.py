# -*- coding: utf-8 -*-

{
    'name': "POS Pizza Modifiers",
    'version': '1.1',
    'summary': 'This Module is a useful odoo addons for customizing your POS Restaurant sales for Pizza and other foods. | Pizza Modifiers | Custmize Pizza | Product Modifiers | PoS Pizza',
    'description': """
This Module is a useful odoo addons for customizing your POS Restaurant sales for Pizza and other foods.
=================
1.1 [IMP] compatible with pos restaurant module.
    """,
    'license': 'OPL-1',
    'author': "Kanak Infosystem LLP",
    'website': "https://kanakinfosystems.com",
    'category': 'Point of Sale',
    'depends': ['sale', 'point_of_sale', 'pos_restaurant'],
    'data': [
        'security/ir.model.access.csv',
        'views/modifires_view.xml',
    ],
    'images': ['static/description/banner.gif'],
    'assets': {
        'point_of_sale.assets': [
            '/pizza_modifiers/static/src/css/style.css',
            '/pizza_modifiers/static/src/js/imageMapResizer.min.js',
            '/pizza_modifiers/static/src/js/db.js',
            '/pizza_modifiers/static/src/js/models.js',
            '/pizza_modifiers/static/src/js/Popups/ModifierProductPopup.js',
            '/pizza_modifiers/static/src/js/Popups/SliceProductPopup.js',
            '/pizza_modifiers/static/src/js/Screens/ProductScreen/ProductScreen.js',
            '/pizza_modifiers/static/src/js/Screens/ProductScreen/Orderline.js',
            '/pizza_modifiers/static/src/js/OrderReceipt.js',
        ],
        'web.assets_qweb': [
            '/pizza_modifiers/static/src/xml/ModifierProductPopup.xml',
            '/pizza_modifiers/static/src/xml/SliceProductPopup.xml',
            '/pizza_modifiers/static/src/xml/Orderline.xml',
            '/pizza_modifiers/static/src/xml/OrderReceipt.xml',
        ],
    },
    'installable': True,
    'application': True,
    'price': 200,
    'currency': 'EUR',
    'live_test_url': 'https://www.youtube.com/watch?v=xDkKGwMbXKU&t=3s',
}
