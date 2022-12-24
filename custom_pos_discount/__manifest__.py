{
    'name': 'Point of Sale Custom Discounts',
    'version': '1.0',
    'category': 'Sales/Point of Sale',
    'sequence': 6,
    'summary': 'Percentage Discounts in the Point of Sale ',
    'description': """

This module allows the cashier to quickly give percentage-based
discount to a customer.

""",
    'depends': ['point_of_sale','pos_discount'],
    'data': [
        'views/custom_pos_discount_views.xml',
        'views/custom_pos_discount_templates.xml'
    ],
    'assets': {
        'point_of_sale.assets': [
            '/custom_pos_discount/static/src/js/CustomDiscountButton.js',
            '/custom_pos_discount/static/src/js/custommodels.js',
        ],
        'web.assets_qweb': [
            'custom_pos_discount/static/src/xml/**/*',
            'custom_pos_discount/static/src/xml/CustomDiscountButton.xml',
        ],
    },

    'installable': True,
}
