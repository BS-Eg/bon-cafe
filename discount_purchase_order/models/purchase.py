# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

import json

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends('order_line.price_total', 'order_line.discount_type',
                 'order_line.discount', 'global_order_discount',
                 'global_discount_type')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = total_discount = 0.0
            for line in order.order_line:
                line._compute_amount()
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                if line.discount_type == 'fixed':
                    total_discount += line.discount
                else:
                    total_discount += line.price_unit * line.product_qty * (
                        (line.discount or 0.0) / 100.0)

            IrConfigPrmtrSudo = self.env['ir.config_parameter'].sudo()
            discTax = IrConfigPrmtrSudo.get_param('account.global_discount_tax')

            if discTax == 'taxed':
                total = amount_untaxed + amount_tax
            else:
                total = amount_untaxed

            if order.global_discount_type == 'fixed':
                total_global_discount = order.global_order_discount
            else:
                total_global_discount = total * (order.global_order_discount or 0.0) / 100
            total -= total_global_discount
            total_discount += total_global_discount

            if discTax != 'taxed':
                total += amount_tax

            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': total,
                'total_global_discount': total_global_discount,
                'total_discount': total_discount,
            })

    total_global_discount = fields.Monetary(string='Total Global Discount', store=True,
                                            readonly=True, compute='_amount_all')
    total_discount = fields.Monetary(string='Total Discount', store=True, readonly=True,
                                     compute='_amount_all', tracking=True)
    global_discount_type = fields.Selection(
        [('fixed', 'Fixed'), ('percent', 'Percent')],
        string="Discount Type",
        default="percent",
        help="If global discount type 'Fixed' has been applied then no partial invoice will be generated for this order.")
    global_order_discount = fields.Float(string='Global Discount', store=True, tracking=True)

    def _prepare_invoice(self):
        self.ensure_one()
        if self.global_order_discount and not self.env.company.discount_account_bill:
            raise UserError(
                _("Global Discount!\nPlease first set account for global discount in purchase setting."))
        if self.global_order_discount and self.global_discount_type == 'fixed':
            lines = self.order_line.filtered(
                lambda l: l.product_id.purchase_method != 'purchase' and l.product_qty != l.qty_received)
            if lines:
                raise UserError(
                    _("This action is going to make bill invoice for the less quantity recieved of this order.\n It will not be allowed because 'Fixed' type global discount has been applied."))
        vals = super(PurchaseOrder, self)._prepare_invoice()
        vals.update({
            'global_discount_type': self.global_discount_type,
            'global_order_discount': self.global_order_discount,
        })
        return vals


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends('price_unit', 'discount_type', 'discount', 'taxes_id', 'product_qty')
    def _get_line_subtotal(self):
        for line in self:
            price = line.price_unit
            quantity = line.product_qty
            taxes = line.taxes_id.compute_all(price, line.order_id.currency_id, quantity,
                                              product=line.product_id, partner=line.order_id.partner_id)
            line.line_sub_total = taxes['total_excluded']

    line_sub_total = fields.Monetary(compute='_get_line_subtotal',
                                     string='Line Subtotal', readonly=True, store=True)
    discount = fields.Float(string='Discount', digits='Discount', default=0.0)
    discount_type = fields.Selection(
        [('fixed', 'Fixed'), ('percent', 'Percent')],
        string="Discount Type",
        default="percent")

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'discount', 'discount_type')
    def _compute_amount(self):
        return super(PurchaseOrderLine, self)._compute_amount()

    # def _prepare_compute_all_values(self):
    #     vals = super(PurchaseOrderLine, self)._prepare_compute_all_values()
    #     price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
    #     quantity = self.product_qty
    #     if self.discount_type == 'fixed':
    #         quantity = 1.0
    #         price = self.price_unit * self.product_qty - (self.discount or 0.0)
    #     vals.update({
    #         'price_unit': price,
    #         'product_qty': quantity,
    #     })
    #     return vals

    def _prepare_compute_all_values(self):
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        quantity = self.product_qty
        if self.discount_type == 'fixed':
            quantity = 1.0
            price = self.price_unit * self.product_qty - (self.discount or 0.0)
        self.ensure_one()
        return {
            'price_unit': price,
            'quantity': quantity,
            'currency': self.order_id.currency_id,
            # 'quantity': self.product_qty,
            'product': self.product_id,
            'partner': self.order_id.partner_id,
        }


    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move=move)
        res.update({
            'discount_type': self.discount_type,
            'discount': self.discount,
        })
        return res