from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    loyalty = fields.Boolean('Eligible for Loyalty')
    loyalty_id = fields.Many2one('loyalty.program', 'Loyalty')
    delivery_partner = fields.Boolean(string='Hide from POS', default=False)
