# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import _, fields, models
from odoo.exceptions import UserError


class PaymentTokenTap(models.Model):
    _inherit = 'payment.token'

    tap_customer_id = fields.Char('Customer ID')

    def _handle_reactivation_request(self):
        """ Override of payment to raise an error informing that Tap tokens cannot be restored.

        More specifically, permanents tokens are never deleted in Tap's backend but we don't
        distinguish them from temporary tokens which are archived at creation time. So we simply
        block the reactivation of every token.

        Note: self.ensure_one()

        :return: None
        :raise: UserError if the token is managed by Tap
        """
        super()._handle_reactivation_request()
        if self.provider != 'tap':
            return

        raise UserError(_("Saved payment methods cannot be restored once they have been archived."))
