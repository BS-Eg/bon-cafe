# -*- coding: utf-8 -*-

##############################################################################
#    Copyright (c) 2021 CDS Solutions SRL. (http://cdsegypt.com)
#    Maintainer: Eng.Ramadan Khalil (<ramadan.khalil@cdsegypt.com>)
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
##############################################################################
from odoo import api, fields, models, _
import logging


class CdsAramexWizard(models.TransientModel):
    _name = "cds.aramex.wizard"

    delivery_uom = fields.Selection(selection=delivery_uom_list, string='UoM')
    pickup_street1 = fields.Char(string="Line 1")
    pickup_street2 = fields.Char(string="Line 2")
    pickup_city = fields.Many2one('res.country.state',
                                  domain=[('country_id.code', '=', 'EG')],
                                  string='City')
    pickup_zone = fields.Char(string="Zone")
    pickup_city_code = fields.Char(string="Bosta City Code")

    receiver_firstname = fields.Char(string="First Name")
    receiver_lastname = fields.Char(string="Last Name")
    receiver_phone = fields.Char(string="Phone")
    receiver_email = fields.Char(string="Email")
    receiver_street1 = fields.Char(string="Line 1")
    receiver_street2 = fields.Char(string="Line 2")
    receiver_city = fields.Many2one('res.country.state',
                                    domain=[('country_id.code', '=', 'EG')],
                                    string='City')
    receiver_zone = fields.Char(string="Zone")
    receiver_city_code = fields.Char(string="Bosta City Code")

    # Shipment Details
    notes = fields.Text(string="Notes")
    businessReference = fields.Char(string="Business Reference")
    cod_amount = fields.Float(string="COD Amount")
    cod_currency = fields.Selection("get_courrency_code",
                                    string="Currency For COD Amount",
                                    default=lambda
                                        self: self.env.user.company_id.currency_id.name)
    # custom_amount = fields.Float(string="Custom Amount")
    # custom_currency = fields.Selection("get_courrency_code", string="Currency For Custom Amount",
    #                                     default=lambda self: self.env.user.company_id.currency_id.name)
    collect_amount = fields.Float(string="Collect Amount")
    collect_currency = fields.Selection("get_courrency_code",
                                        string="Currency For Collect Amount",
                                        default=lambda
                                            self: self.env.user.company_id.currency_id.name)
    cash_additional_amount = fields.Float(string="Cash Additional Amount")
    cash_additional_currency = fields.Selection("get_courrency_code",
                                                string="Currency For Cash Additional Amount",
                                                default=lambda
                                                    self: self.env.user.company_id.currency_id.name)

    picking_id = fields.Many2one('stock.picking', string="Picking",
                                 default=_get_active_id, required=1)

    @api.onchange('pickup_city')
    def _onchange_pickup(self):
        self.pickup_city_code = self.picking_id.carrier_id.get_city_code(
            self.pickup_city.code)

    @api.onchange('receiver_city')
    def _onchange_receiver(self):
        self.receiver_city_code = self.picking_id.carrier_id.get_city_code(
            self.receiver_city.code)

    def apply(self):
        self.ensure_one()
        ctx = self._context.copy()
        # TODO:we disable the validation of the negative cod
        # if self.cod_amount <= 0.0:
        #    raise UserError(_('COD Amount must be grater than 0.0 for Service Type "Cash On Delivery".'))

        picking_obj = self.env["stock.picking"].browse(
            self._context["active_id"]) if self._context.get(
            'active_model') and self._context[
                                               "active_model"] == "stock.picking" and self._context.get(
            'active_id') else \
            self.env["stock.picking"]

        vals = {
            # Pickup Address
            "pickup_street1": self.pickup_street1,
            "pickup_street2": self.pickup_street2 or "",
            "pickup_city": self.pickup_city.name,
            "pickup_zone": self.pickup_zone,
            "pickup_city_code": self.pickup_city_code,

            # Receiver Details
            "receiver_firstname": self.receiver_firstname,
            "receiver_lastname": self.receiver_lastname,
            "receiver_phone": self.receiver_phone,
            "receiver_email": self.receiver_email,
            "receiver_street1": self.receiver_street1,
            "receiver_street2": self.receiver_street2 or "",
            "receiver_city": self.receiver_city.name,
            "receiver_zone": self.receiver_zone,
            "receiver_city_code": self.receiver_city_code,

            # Shipment Details
            "notes": self.notes,
            "businessReference": self.businessReference,
            "cod_amount": self.cod_amount,
            "cod_currency": self.cod_currency,
            "collect_amount": self.collect_amount,
            "collect_currency": self.collect_currency,
            "cash_additional_amount": self.cash_additional_amount,
            "cash_additional_currency": self.cash_additional_currency,

            # Picking Id
            "picking_id": picking_obj,
        }
        return picking_obj.with_context(
            {"Testing": True, 'vals_for_shipping': vals}).send_to_shipper()
