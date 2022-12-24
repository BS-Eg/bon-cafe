from odoo import api, fields, models, tools, _
import logging

_logger = logging.getLogger(__name__)


class Inherit_PosPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

   
    custom_image_1920 = fields.Image("Image")

    