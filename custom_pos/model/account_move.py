from odoo import api, fields, models, tools, _
import logging

_logger = logging.getLogger(__name__)


class InheritAccountMoveLine(models.Model):
    _inherit = "account.move.line"

    custom_note = fields.Text(string='Note')
    delivery_partner_id = fields.Many2one('res.partner',string='Delivery Partner')

