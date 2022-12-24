# -*- coding: utf-8 -*-

##############################################################################
#    Copyright (c) 2021 CDS Solutions SRL. (http://cdsegypt.com)
#    Maintainer: Eng.Ramadan Khalil (<ramadan.khalil@cdsegypt.com>)
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
##############################################################################

from odoo import fields, models, api, _
from odoo.exceptions import Warning, ValidationError, UserError
import json
import requests


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    aramex_label_url = fields.Char('Aramex Label URL')
    tracking_status = fields.Char(string="Tracking Status", copy=False)

    @api.model
    def update_aramex_tracking_status(self):
        aramex_end_status = ['Delivered',
                             'Returned to Shipper',
                             'Order Cancelled'
                             ]
        picking_ids = self.search([('carrier_id.delivery_type', '=', 'aramex'),
                                   ('state', '=', 'done'),
                                   ('carrier_tracking_ref', '!=', False),
                                   ('tracking_status', 'not in', aramex_end_status),('tracking_status','not like','Shipment Update:COD Transferred')
                                   ],order='id desc',limit=1000)



        carrier_ids = picking_ids.mapped('carrier_id')
        for carrier in carrier_ids:
            carrier_picks = picking_ids.filtered(
                lambda p: p.carrier_id == carrier and p.carrier_tracking_ref and 'COD Transferred' not in p.carrier_tracking_ref)
            carrier.aramex_update_tracking_status(carrier_picks)
