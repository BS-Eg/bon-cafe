# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResBranch(models.Model):
    _name = 'res.branch'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Branch'

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one('res.company', required=True, tracking=True)
    telephone = fields.Char(string='Telephone No', tracking=True)
    address = fields.Text('Address', tracking=True)
