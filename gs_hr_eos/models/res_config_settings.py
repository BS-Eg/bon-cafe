# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class ResConfigSettingsInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    journal_id = fields.Many2one('account.journal', copy=False)
    account_id = fields.Many2one('account.account', copy=False)

    def set_values(self):
        res = super(ResConfigSettingsInherit, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("gs_hr_eos.journal_id", self.journal_id.id)
        self.env['ir.config_parameter'].sudo().set_param("gs_hr_eos.account_id", self.account_id.id)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettingsInherit, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        journal_id = params.get_param('gs_hr_eos.journal_id')
        account_id = params.get_param('gs_hr_eos.account_id')
        res.update(
            journal_id=int(journal_id),
            account_id=int(account_id),
        )
        return res

