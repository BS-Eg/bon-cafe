# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

{
    'name': 'Tap Payment Gateway',
    'category': 'Accounting/Payment Acquirers',
    'version': '15.0.1.0',
    'summary': '''
Tap Payment Gateway module is used in payment method to simplifies online payment.
KNET | MADA | BENEFIT | Oman Net | Apple Pay | Visa | Mastercard | meeza | Amex
Refund | Subscription | Save Card | Use save card to pay
    ''',
    'description': """Tap Payment Gateway module is used in payment method to simplifies online payment.""",
    'author': 'Kanak Infosystems LLP.',
    'website': 'https://www.kanakinfosystems.com',
    'depends': ['payment'],
    'images': ['static/description/banner.jpg'],
    'data': [
        'data/payment_acquirer_cron_data.xml',
        'views/payment_acquirer_views.xml',
        'views/payment_acquirer_templates.xml',
        'data/payment_acquirer_data.xml',
    ],
    'license': 'OPL-1',
    'sequence': 1,
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 56,
    'currency': 'EUR',
    'uninstall_hook': 'uninstall_hook',
    'live_test_url': 'https://youtu.be/E0nGn_s7Mc0',
}
