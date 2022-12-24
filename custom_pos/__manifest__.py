# -*- coding: utf-8 -*-
{
    'name': "Custom Pos",

    'summary': """
     custom pos in agwatlls
       """,

    'description': """
        custom pos in agwatllc.
    """,
    'author': "Techspawn Solutions Pvt. Ltd.",
    'website': "http://www.techspawn.com",
    'category': 'Sale',
    'version': '14.0.0',
    'depends': ['base',
                'point_of_sale', 'custom_pos_discount'],
    'data': [
        'views/custom_filter.xml',
        'views/point_of_sale.xml',
        'views/account_move.xml',
        'views/invoice_report.xml',
        'views/res_partner.xml',
        'views/pos_order_form.xml',
        'views/report_saledetails.xml',
        'views/pos_payment_method.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'custom_pos/static/src/js/db.js',
            'custom_pos/static/src/js/pos.js',
            'custom_pos/static/src/js/Loyalty.js',
            'custom_pos/static/src/js/ClientListScreen.js',
            'custom_pos/static/src/js/PaymentScreen_new.js',
            'custom_pos/static/src/js/ProductScreen.js',
            'custom_pos/static/src/js/NumberBuffer.js',
            'custom_pos/static/src/js/NumberPopupTourMethods.js',
        ],
        'web.assets_qweb': [
            'custom_pos/static/src/xml/**/*',
            'custom_pos/static/src/xml/PaymentScreen.xml',
            'custom_pos/static/src/xml/pos_order_receipt.xml',
            'custom_pos/static/src/xml/ClientListScreen.xml',
            'custom_pos/static/src/xml/NumberPopup.xml',
            'custom_pos/static/src/xml/NumpadWidget.xml',
            'custom_pos/static/src/xml/ClientLine.xml',
            'custom_pos/static/src/xml/PaymentMethodButton.xml',
            'custom_pos/static/src/xml/PaymentScreenPaymentLines.xml',
        ],
    },

    'demo': [
    ],
}
