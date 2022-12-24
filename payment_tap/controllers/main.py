# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

import json
import logging
import pprint
import requests
import werkzeug

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class TapController(http.Controller):
    _return_url = '/payment/tap/return/'
    _refund_url = '/payment/tap/refund/'

    @http.route(_return_url, type='http', auth='public', csrf=False, save_session=False)
    def tap_return_feedback(self, **post):
        tap_id = http.request.params.get('tap_id')
        url = "https://api.tap.company/v2/charges/%s" % tap_id
        acquirer_id = request.env['payment.acquirer'].sudo().search([('provider', '=', 'tap')], limit=1)
        headers = {'authorization': 'Bearer %s' % acquirer_id.tap_secret_key}
        response = requests.request("GET", url, data="{}", headers=headers)
        data = json.loads(response.text)
        _logger.info('Tap: entering return feedback with post data %s', pprint.pformat(data))
        request.env['payment.transaction'].sudo()._handle_feedback_data('tap', data)
        return werkzeug.utils.redirect('/payment/status')

    @http.route([_refund_url], type='json', auth='public', csrf=False)
    def tap_refund_feedback(self, **post):
        _logger.info('Tap: entering refund feedback with post data %s', pprint.pformat(post))
        request.env['payment.transaction'].sudo()._handle_feedback_data('tap', post)
        return True
