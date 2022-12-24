# -*- coding: utf-8 -*-

##############################################################################
#    Copyright (c) 2021 CDS Solutions SRL. (http://cdsegypt.com)
#    Maintainer: Eng.Ramadan Khalil (<ramadan.khalil@cdsegypt.com>)
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
##############################################################################

import datetime
import requests
from werkzeug.urls import url_join
import requests
import json

from odoo import _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round, float_is_zero

ARAMEX_TEST_URL = 'https://ws.dev.aramex.net/ShippingAPI.V2'
ARAMEX_PROD_URL = 'https://ws.aramex.net/ShippingAPI.V2'
RATE_ENDPOINT = 'RateCalculator/Service_1_0.svc/json/CalculateRate'
SHIPPING_ENDPOINT = 'Shipping/Service_1_0.svc/json'
TRACKING_ENDPOINT = 'Tracking/Service_1_0.svc/json'
import logging

_logger = logging.getLogger()

ADDRESS_DICT = {
    "Line1": "",
    "Line2": "",
    "Line3": "",
    "City": "",
    "StateOrProvinceCode": "",
    "PostCode": "",
    "CountryCode": "",
    "Longitude": 0,
    "Latitude": 0,
    "BuildingNumber": None,
    "BuildingName": None,
    "Floor": None,
    "Apartment": None,
    "POBox": None,
    "Description": None
}


class AramexRequest():

    def __init__(self, prod_environment, debug_logger,
                 username,
                 password,
                 account_no,
                 account_pin,
                 country_code,
                 entity):
        self.debug_logger = debug_logger
        if not prod_environment:
            self.url = ARAMEX_PROD_URL
        else:
            self.url = ARAMEX_TEST_URL
        client_info = {
            "UserName": username,
            "Password": password,
            "Version": "v1",
            "AccountNumber": account_no,
            "AccountPin": account_pin,
            "AccountEntity": entity,
            "AccountCountryCode": country_code,
            "Source": 24
        }
        self.client_info = client_info
        self.rate_shipment_details = {}
        self.shipment_request = {}
        self.prod_environment = prod_environment

    def _get_partner_data(self, partner):

        city = ""
        if partner.city_id:
            city = partner.city_id.name
        elif partner.city:
            city = partner.city
        # return city
        country_code = partner.country_id.code
        address = partner.street or ""
        if partner.street2:
            address += ',%s' % partner.street2
        data = {
            "Line1": partner.street or "",
            "Line2": partner.street2 or "",
            "City": city,
            "CountryCode": country_code,

        }
        return data

    def _set_rate_origin_address(self, partner):
        """"""
        rate_origin_address = ADDRESS_DICT.copy()
        partner_data = self._get_partner_data(partner)
        rate_origin_address.update(partner_data)
        self.rate_origin_address = rate_origin_address

    def _set_rate_dest_address(self, partner):
        rate_dest_address = ADDRESS_DICT.copy()
        partner_data = self._get_partner_data(partner)
        rate_dest_address.update(partner_data)
        self.rate_dest_address = rate_dest_address

    def check_required_value(self, carrier, recipient, shipper, order=False,
                             picking=False):
        carrier = carrier.sudo()
        recipient_required_field = [ 'state_id', 'country_id']
        if not carrier.aramex_account_number:
            return _(
                "ARAMEX account number is missing, please modify your delivery method settings.")
        if not carrier.aramex_account_pin:
            return _(
                "ARAMEX account PIN is missing, please modify your delivery method settings.")
        if not carrier.aramex_account_user:
            return _(
                "ARAMEX Username is missing, please modify your delivery method settings.")
        if not carrier.aramex_account_password:
            return _(
                "ARAMEX Password is missing, please modify your delivery method settings.")

        if not recipient.street and not recipient.street2:
            recipient_required_field.append('street')
        res = [field for field in recipient_required_field if
               not recipient[field]]
        if res:
            return _(
                "The address of the customer is missing or wrong (Missing field(s) :\n %s)") % ", ".join(
                res).replace("_id", "")

        shipper_required_field = ['city', 'phone', 'country_id', 'email']
        if not shipper.street and not shipper.street2:
            shipper_required_field.append('street')

        res = [field for field in shipper_required_field if not shipper[field]]
        if res:
            return _(
                "The address of your company warehouse is missing or wrong (Missing field(s) :\n %s)") % ", ".join(
                res).replace("_id", "")

        if order:
            if not order.order_line:
                return _("Please provide at least one item to ship.")

        return False

    def _process_aramex_rating(self):
        rate_url = "{}/{}".format(self.url, RATE_ENDPOINT)
        rate_data = {
            'ClientInfo': self.client_info,
            'OriginAddress': self.rate_origin_address,
            'DestinationAddress': self.rate_dest_address,
            'ShipmentDetails': self.rate_shipment_details,
            'Transaction': None
        }
        rate_data_json = json.dumps(rate_data)
        rate_headers = {'content-type': 'application/json',
                        'Accept': 'application/json'}
        rate_response = requests.request('POST', url=rate_url,
                                         data=rate_data_json,
                                         headers=rate_headers,
                                         timeout=60)
        print(rate_response.json())
        return rate_response

    def _process_aramex_create_shipment(self):
        url = "{}/{}/CreateShipments".format(self.url, SHIPPING_ENDPOINT)
        shipment_data = {
            'ClientInfo': self.client_info,
            'Shipments': self.shipment_request,
            "Transaction": {
                "Reference1": "",
                "Reference2": "",
                "Reference3": "",
                "Reference4": "",
                "Reference5": ""
            }
        }
        _logger.info('ARAMEX SHIPMENT REQUEST')

        shipment_json = json.dumps(shipment_data)
        _logger.info(shipment_json)

        headers = {'content-type': 'application/json',
                   'Accept': 'application/json'}
        response = requests.request('POST', url=url,
                                    data=shipment_json,
                                    headers=headers,
                                    timeout=60)

        return response

    def _process_print_label(self, tracking):
        url = "{}/{}/PrintLabel".format(self.url, SHIPPING_ENDPOINT)
        label_data = {
            'ClientInfo': self.client_info,
            "LabelInfo": {
                "ReportID": 9729,
                "ReportType": "URL"
            },
            "ShipmentNumber": tracking
        }

        label_data = json.dumps(label_data)
        headers = {'content-type': 'application/json',
                   'Accept': 'application/json'}
        response = requests.request('POST', url=url,
                                    data=label_data,
                                    headers=headers,
                                    timeout=60)
        response_json = response.json()
        label_url = response_json.get('ShipmentLabel').get('LabelURL')

        return label_url

    def _process_track_shipment(self, trackings,last=True):
        url = "{}/{}/TrackShipments".format(self.url, TRACKING_ENDPOINT)
        label_data = {
            'ClientInfo': self.client_info,
            'GetLastTrackingUpdateOnly':last,
            "Shipments": trackings,

        }

        label_data = json.dumps(label_data)
        headers = {'content-type': 'application/json',
                   'Accept': 'application/json'}
        response = requests.request('POST', url=url,
                                    data=label_data,
                                    headers=headers,
                                    timeout=60)
        if response.status_code==200:

            response_json = response.json()
            statuses = response_json.get('TrackingResults')
            print(response_json)
            return statuses

        else:
            return []
        # label_url = response_json.get('ShipmentLabel').get('LabelURL')
        #
        # return label_url
