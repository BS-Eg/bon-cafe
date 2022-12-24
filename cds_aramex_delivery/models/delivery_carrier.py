# -*- coding: utf-8 -*-

##############################################################################
#    Copyright (c) 2021 CDS Solutions SRL. (http://cdsegypt.com)
#    Maintainer: Eng.Ramadan Khalil (<ramadan.khalil@cdsegypt.com>)
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date
from .aramex_request import AramexRequest
import time
from dateutil.relativedelta import relativedelta

ARAMEX_TEST_URL = 'https://ws.dev.aramex.net/ShippingAPI.V2'
ARAMEX_PROD_URL = 'https://ws.aramex.net/ShippingAPI.V2'

ARAMEX_TRACKING_URL = "https://www.aramex.com/express/track-results-multiple.aspx?ShipmentNumber="
import logging

_logger = logging.getLogger()


class AramexStatePrice(models.Model):
    _name = 'aramex.state.price'
    state_id = fields.Many2one('res.country.state',
                               string='City')
    price = fields.Float(string="Price")
    carrier_id = fields.Many2one('delivery.carrier')


class ProviderAramex(models.Model):
    _inherit = 'delivery.carrier'

    PAYMENT_TYPE = [('P', 'Prepaid'),
                    ('C', 'Collect'),
                    ('T', 'Third Party')]
    PRODUCT_TYPE = [('PDX', 'Priority Document Express'),
                    ('PPX', 'Priority Parcel Express'),
                    ('EPX', 'Economy Parcel Express'),
                    ('PLX', 'Priority Letter Express'),
                    ('DDX', 'Deferred Document Express'),
                    ('DPX', 'Deferred Parcel Express'),
                    ('GDX', 'Ground Document Express'),
                    ('GPX', 'Ground Parcel Express'),
                    ('CDS', 'Special Credit Card Delivery')]
    PRODUCT_GROUP = [('EXP', 'Express'),
                     ('DOM', 'Domestic')]

    ARAMEX_SERVICES = [('CODS', 'Cash on Delivery'),
                       ('RTRN', 'Return'),
                       ('CODS,RTRN', 'COD & Return'),
                       ('SIG', 'Signature Required'),
                       ('FIRST', 'First Delivery')]

    ARAMEX_COUNTRIES = [('EG', 'EG'),('SA','SA')]

    delivery_type = fields.Selection(selection_add=[
        ('aramex', "Aramex")
    ], ondelete={'aramex': lambda recs: recs.write(
        {'delivery_type': 'fixed', 'fixed_price': 0})})
    aramex_account_user = fields.Char('Aramex User Name')
    aramex_account_password = fields.Char('Aramex Password')
    aramex_account_number = fields.Char('Aramex Account Number')
    aramex_account_entity = fields.Char('Aramex Account Entity')
    aramex_account_pin = fields.Char('Aramex Account PIN')
    aramex_account_country = fields.Selection(ARAMEX_COUNTRIES,
                                              'Aramex Country COD')
    aramex_payment_type = fields.Selection(PAYMENT_TYPE, string='Payment Type')
    aramex_product_type = fields.Selection(PRODUCT_TYPE, string='Product Type')
    aramex_product_group = fields.Selection(PRODUCT_GROUP,
                                            string='Product Group')
    aramex_service_type = fields.Selection(ARAMEX_SERVICES,
                                           string='Service Type')
    aramex_rate_type = fields.Selection(
        selection=[('loc', 'Local'), ('api', 'API')],
        string='Rates Source', default='loc')
    aramex_price_line_ids = fields.One2many(comodel_name='aramex.state.price',
                                            inverse_name='carrier_id',
                                            string='Aramex Local Prices')
    aramex_cod_currency = fields.Many2one('res.currency','COD Currency ')
    aramex_delivery_note = fields.Text('Aramex Delivery Notes')

    def aramex_get_cod_amount(self, picking=False):

        amount = 0
        if picking and picking.sale_id:
            amount = picking.sale_id.amount_total
        return amount

    def aramex_get_delivery_note(self,picking):
        self.ensure_one()
        delivery_note = ''
        product_desc = []
        for ml in picking.move_lines:
            line_description = '[{}]({})\n'.format(
                ml.product_id.default_code,

                ml.product_uom_qty)
            product_desc.append(line_description)
        products_description = '+'.join(product_desc)

        delivery_note += products_description

        if self.aramex_delivery_note:
            delivery_note += '++' + self.aramex_delivery_note
        return delivery_note

    def get_aramex_api_request(self):
        return AramexRequest(prod_environment=self.prod_environment,
                             debug_logger=self.log_xml,
                             username=self.aramex_account_user,
                             password=self.aramex_account_password,
                             account_no=self.aramex_account_number,
                             account_pin=self.aramex_account_pin,
                             country_code=self.aramex_account_country,
                             entity=self.aramex_account_entity)

    def _get_aramex_shipper_data(self, picking):
        acc_number = self.aramex_account_number
        ref = picking.name
        ref2 = ''
        if picking.sale_id:
            ref2 = picking.sale_id.name

        shipper_partner = picking.picking_type_id.warehouse_id.partner_id
        if not shipper_partner:
            raise ValidationError(
                _('Please set address to your company warehouse'))
        sh_city = shipper_partner.city_id.name or shipper_partner.city
        if not sh_city:
            raise ValidationError(_('Please set you warehouse City'))
        phone = shipper_partner.phone or shipper_partner.mobile
        if not phone:
            raise ValidationError(
                _('Please set your warehouse Phone or mobile'))
        mobile = shipper_partner.mobile or shipper_partner.phone
        if not mobile:
            raise ValidationError(_('Please set your warehouse Mobile Number'))
        email = shipper_partner.email
        if not email:
            raise ValidationError(_('Please set Your company  E-mail address'))
        shipper_data = {
            "Reference1": ref2,
            "Reference2": ref,
            "AccountNumber": acc_number,
            "PartyAddress": {
                "Line1": shipper_partner.street or '',
                "Line2": shipper_partner.street2 or '',
                "Line3": "",
                "City": sh_city,
                "StateOrProvinceCode": shipper_partner.zip or '',
                "PostCode": "",
                "CountryCode": shipper_partner.country_id.code,
                "Longitude": 0,
                "Latitude": 0,
                "BuildingNumber": False,
                "BuildingName": False,
                "Floor": False,
                "Apartment": False,
                "POBox": False,
                "Description": False
            },
            "Contact": {
                "Department": "",
                "PersonName": shipper_partner.name,
                "Title": "",
                "CompanyName": shipper_partner.name,
                "PhoneNumber1": shipper_partner.phone,
                "PhoneNumber1Ext": "",
                "PhoneNumber2": "",
                "PhoneNumber2Ext": "",
                "FaxNumber": "",
                "CellPhone": shipper_partner.mobile,
                "EmailAddress": shipper_partner.email,
                "Type": ""
            }
        }
        return shipper_data

    def _get_aramex_consignee_info(self, picking):

        partner_id = picking.partner_id
        city = partner_id.city_id.name
        customer_parents = self.env['res.partner'].search(
            [('id', 'parent_of', partner_id.id)])
        if not city and partner_id.city:
            city = partner_id.city
        if not city and customer_parents.mapped('city_id'):
            city = customer_parents.mapped('city_id')[0].name




        phone = partner_id.phone or partner_id.mobile
        if not phone and customer_parents.mapped('phone'):
            phone = customer_parents.mapped('phone')[0]
        mobile = partner_id.mobile or partner_id.phone
        email = partner_id.email
        if not email and customer_parents.mapped('email'):
            email = customer_parents.mapped('email')[0]
        customer_info = {'city': city,
                         'phone': phone,
                         'email': email,
                         'mobile': mobile}

        return customer_info

    def _get_aramex_consignee_data(self, picking):
        partner_id = picking.partner_id
        customer_info = self._get_aramex_consignee_info(picking)
        city = customer_info.get('city')
        phone = customer_info.get('phone')
        mobile = customer_info.get('mobile')
        email = customer_info.get('email')
        if not city:
            raise ValidationError(_('Please set you Customer City'))

        if not phone:
            raise ValidationError(_('Please set customer Phone or mobile'))

        if not mobile:
            raise ValidationError(_('Please set customer Mobile Number'))

        if not email:
            raise ValidationError(_('Please set customer E-mail address'))
        consignee_data = {
            "Reference1": "",
            "Reference2": "",
            "AccountNumber": "",
            "PartyAddress": {
                "Line1": partner_id.street or '',
                "Line2": partner_id.street2 or '',
                "Line3": "",
                "City": city,
                "StateOrProvinceCode": partner_id.zip or '',
                "PostCode": "",
                "CountryCode": partner_id.country_id.code or 'EG',
                "Longitude": 0,
                "Latitude": 0,
                "BuildingNumber": "",
                "BuildingName": "",
                "Floor": "",
                "Apartment": "",
                "POBox": False,
                "Description": ""
            },
            "Contact": {
                "Department": "",
                "PersonName": partner_id.name,
                "Title": "",
                "CompanyName": partner_id.name,
                "PhoneNumber1": phone or mobile,
                "PhoneNumber1Ext": "",
                "PhoneNumber2": "",
                "PhoneNumber2Ext": "",
                "FaxNumber": "",
                "CellPhone": mobile or phone,
                "EmailAddress": email,
                "Type": ""
            }
        }
        return consignee_data

    def _get_aramex_shipment_details(self, order=False, pick=False):
        weight, number = self._get_aramex_product_weight(order=order, pick=pick)

        cod_amount = None
        if self.aramex_service_type and 'CODS' in self.aramex_service_type and self.aramex_cod_currency:
            cod_amount = None
            cod_value = self.aramex_get_cod_amount(pick)
            if cod_value > 0:
                cod_amount = {
                    "CurrencyCode": self.aramex_cod_currency.name,
                    "Value": cod_value}

        delivery_note = ''
        if pick:
            delivery_note = self.aramex_get_delivery_note(pick)
        custom_value = None
        if self.aramex_product_type =='EPX':
            custom_value={
                "CurrencyCode": 'USD',
                "Value": 5}

        shipment_details = {
            "ProductGroup": self.aramex_product_group,
            "ProductType": self.aramex_product_type or "PPX",
            "PaymentType": self.aramex_payment_type or "P",
            "NumberOfPieces": number,
            "DescriptionOfGoods": delivery_note,
            "GoodsOriginCountry": None,
            "PaymentOptions": None,
            "Dimensions": None,
            "ActualWeight": {
                "Unit": "kg",
                "Value": weight
            },
            "ChargeableWeight": None,
            "CustomsValueAmount": custom_value,
            "CashOnDeliveryAmount": cod_amount,
            "InsuranceAmount": None,
            "CashAdditionalAmount": None,
            "CashAdditionalAmountDescription": None,
            "CollectAmount": None,
            "Services": self.aramex_service_type if self.aramex_service_type and cod_amount != None else '',
            "Items": None,
            "DeliveryInstructions": None,
            "AdditionalProperties": None

        }
        return shipment_details

    def _get_aramex_shipments(self, picking):
        shipper_data = self._get_aramex_shipper_data(picking)
        consignee_data = self._get_aramex_consignee_data(picking)
        shipment_details = self._get_aramex_shipment_details(pick=picking)
        shipment_date = (int(
            (datetime.now() + relativedelta(days=1)).timestamp()) * 1000)
        ref = picking.sale_id and picking.sale_id.name or ''

        shipments = [{
            "Reference1": ref,
            "Reference2": "",
            "Reference3": "",
            "Shipper": shipper_data,
            "Consignee": consignee_data,
            "ShippingDateTime": "/Date(%s)/" % shipment_date,
            "DueDate": "/Date(%s)/" % shipment_date,
            "ThirdParty": None,
            "Comments": "",
            "PickupLocation": "",
            "OperationsInstructions": "",
            "AccountingInstrcutions": "",
            "Details": shipment_details,
            "Attachments": [],
            "ForeignHAWB": "",
            "TransportType ": 0,
            "PickupGUID": "",
            "Number": None,
            "ScheduledDelivery": None
        }]
        return shipments


    def aramex_send_shipping(self, pickings):
        res = []
        aramex = self.get_aramex_api_request()
        for pick in pickings:
            shipment_request = self._get_aramex_shipments(pick)
            aramex.shipment_request = shipment_request
            shipment_response = aramex._process_aramex_create_shipment()
            response_data = shipment_response.json()
            _logger.info("ARAMEX RESPONSE")
            _logger.info(response_data)
            if response_data.get('HasErrors'):
                error_msg = ''
                error_code = ''
                if response_data.get('Shipments'):
                    error_msg = \
                        response_data['Shipments'][0]['Notifications'][0][
                            'Message']
                    error_code = \
                        response_data['Shipments'][0]['Notifications'][0][
                            'Code']

                raise ValidationError(_(
                    'Error While sending shipment to aramex as the following error :'
                    '\n Error Code : {} \n'
                    'Error Message: {}  '.format(
                        error_code, error_msg)))
            print(shipment_response)
            tracking_number = response_data.get('Shipments')[0].get('ID')
            aramex_label_url = aramex._process_print_label(
                tracking=tracking_number)
            pick.aramex_label_url = aramex_label_url
            msg = (_(
                "Shipment created into ARAMEX <br/> <b>Tracking Number : </b>%s") % (
                       tracking_number))

            msg += _(
                '<br/>Please Download the AWB pdf From The Following URL : '
                '<a target="_blank" href="{}">{}</a>'.format(aramex_label_url,
                                                             tracking_number))
            pick.message_post(body=msg)
            shipping_data = {
                'exact_price': 0,
                'tracking_number': tracking_number,
            }

            res = res + [shipping_data]
        return res

    def aramex_rate_shipment(self, order):
        res = self._aramex_rate_shipment_vals(order=order)
        return res

    def _get_aramex_product_weight(self, order=False, pick=False):
        total_weight = 0
        number = 0
        if order:
            for line in order.order_line.filtered(
                    lambda l: l.product_id.type == 'product'):
                number += line.product_uom_qty
                total_weight = (line.product_id.weight * line.product_uom_qty)
            if number <= 0:
                number = 1
            if total_weight <= 0:
                total_weight = 1
        elif pick:
            for move in pick.move_lines.filtered(
                    lambda l: l.product_id.type == 'product'):
                number += move.quantity_done
                total_weight = (move.product_id.weight * move.quantity_done)
            if number <= 0:
                number = 1
            if total_weight <= 0:
                total_weight = 1

        return total_weight, number

    def _aramex_rate_shipment_vals(self, order=False, picking=False):
        if picking:
            warehouse_partner_id = picking.picking_type_id.warehouse_id.partner_id
            destination_partner_id = picking.partner_id
        else:
            warehouse_partner_id = order.warehouse_id.partner_id
            destination_partner_id = order.partner_id

        aramex = self.get_aramex_api_request()
        check_value = aramex.check_required_value(self, destination_partner_id,
                                                  warehouse_partner_id,
                                                  order=order, picking=picking)
        if check_value:
            return {'success': False,
                    'price': 0.0,
                    'error_message': check_value,
                    'warning_message': False}

        aramex._set_rate_origin_address(warehouse_partner_id)
        aramex._set_rate_dest_address(destination_partner_id)
        aramex.rate_shipment_details = self._get_aramex_shipment_details(
            order=order)

        if self.aramex_rate_type == 'loc':
            price_line = self.aramex_price_line_ids.filtered(
                lambda l: l.state_id == destination_partner_id.state_id)
            if not price_line:
                error_msg = 'Couldn`t find state %s in aramex local rates please configure it' % destination_partner_id.state_id.name
                return {
                    'success': False,
                    'price': 0.0,
                    'error_message': error_msg,
                    'warning_message': True,
                }
            else:
                return {
                    'success': True,
                    'price': price_line.price,
                    'error_message': "",
                    'warning_message': False,
                }
        else:
            response = aramex._process_aramex_rating()
            return {
                'success': False,
                'price': 0.0,
                'error_message': "",
                'warning_message': False,
            }

    def aramex_cancel_shipment(self, pickings):
        pass
        # pickings.write(
        #     {'carrier_tracking_ref': '', 'tracking_status': 'Canceled'
        #      })

    def aramex_get_tracking_link(self, pick):
        track_url = ARAMEX_TRACKING_URL + pick.carrier_tracking_ref
        return track_url

    def aramex_get_default_custom_package_code(self):
        pass

    def aramex_update_tracking_status(self, pickings):
        if not pickings:
            return ''
        aramex = self.get_aramex_api_request()

        done_picking = self.env['stock.picking']
        while True:
            todo_picking = self.env['stock.picking'].search(
                [('id', 'in', pickings.ids),
                 ('id', 'not in', done_picking.ids)], limit=20)
            trackings = todo_picking.mapped('carrier_tracking_ref')
            done_picking += todo_picking
            if not todo_picking:
                break
            picking_status = aramex._process_track_shipment(trackings=trackings,last=True)
            for status in picking_status:
                picking_id = todo_picking.filtered(
                    lambda p: p.carrier_tracking_ref == status.get('Key'))
                if picking_id:
                    aramex_state_code = status.get('Value') and \
                                        status.get('Value')[
                                            0].get('UpdateCode')
                    aramex_state = status.get('Value') and status.get('Value')[
                        0].get('UpdateDescription')
                    if aramex_state_code:
                        comment = status.get('Value') and status.get('Value')[
                            0].get('Comments')
                        if aramex_state_code == 'SH382' and comment:
                            aramex_state += ':{}'.format(comment)
                    _logger.info(
                        'ARAMEX STATUS ====> Picking : {}  Status : {}'.format(
                            picking_id.name, aramex_state))
                    picking_id.tracking_status = aramex_state
