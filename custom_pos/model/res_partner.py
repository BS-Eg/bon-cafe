from odoo import api, fields, models, tools, _
import logging

_logger = logging.getLogger(__name__)


class Customer(models.Model):
    _inherit = "res.partner"
    

    delivery_partner = fields.Boolean(string='Delivery Partner')

    