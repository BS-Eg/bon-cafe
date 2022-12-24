from odoo import models, fields


class LoyaltyRule(models.Model):
    _inherit = 'loyalty.rule'

    max_amount = fields.Float('Maximum amount')
    min_amount = fields.Float('Minimmum amount')
