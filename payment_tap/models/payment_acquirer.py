# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import api, fields, models


class PaymentAcquirerTap(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('tap', 'Tap')], ondelete={'tap': 'set default'})
    tap_secret_key = fields.Char(string='Secret Key', required_if_provider='tap', groups='base.group_user')
    tap_publishable_key = fields.Char(string='Publishable Key', required_if_provider='tap', groups='base.group_user')
    tap_payment_options = fields.Selection([
        ('src_all', 'All'),
        ('src_card', 'Card Payment'),
        ('src_kw.knet', 'KNET'),
        ('src_bh.benefit', 'BENEFIT'),
        ('src_sa.mada', 'MADA'),
        ('src_om.omannet', 'Oman Net'),
        ('src_apple_pay', 'Apple Pay')], string='Payment Options', required_if_provider='tap', default="src_all", groups='base.group_user')
    tap_use_3d_secure = fields.Boolean('Use 3D Secure', groups='base.group_user')

    @api.model
    def _get_compatible_acquirers(self, *args, currency_id=None, **kwargs):
        """ Override/ of payment to unlist Tap acquirers for unsupported currencies. """
        acquirers = super()._get_compatible_acquirers(*args, currency_id=currency_id, **kwargs)
        currency = self.env['res.currency'].browse(currency_id).exists()
        if currency and currency.name not in ["AED", "BHD", "EGP", "EUR", "GBP", "KWD", "OMR", "QAR", "SAR", "USD"]:
            acquirers = acquirers.filtered(
                lambda a: a.provider != 'tap'
            )
        else:
            for acquirer in acquirers.filtered(lambda a: a.provider == 'tap'):
                if acquirer.tap_payment_options == 'src_card' and currency.name not in ["AED", "BHD", "EGP", "EUR", "GBP", "KWD", "OMR", "QAR", "SAR", "USD"]:
                    acquirers = acquirers - acquirer
                elif acquirer.tap_payment_options == 'src_kw.knet' and currency.name != 'KWD':
                    acquirers = acquirers - acquirer
                elif acquirer.tap_payment_options == 'src_bh.benefit' and currency.name != 'BHD':
                    acquirers = acquirers - acquirer
                elif acquirer.tap_payment_options == 'src_sa.mada' and currency.name != 'SAR':
                    acquirers = acquirers - acquirer
                elif acquirer.tap_payment_options == 'src_om.omannet' and currency.name != 'OMR':
                    acquirers = acquirers - acquirer
        return acquirers

    def _get_default_payment_method_id(self):
        self.ensure_one()
        if self.provider != 'tap':
            return super()._get_default_payment_method_id()
        return self.env.ref('payment_tap.payment_method_tap').id
