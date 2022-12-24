# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class GsSetRenewWizard(models.TransientModel):
    _name = "set.renew.wizard"

    def action_set_renew(self):
        active_id = self.env.context.get('active_id')
        contract = self.env['hr.contract'].search([('id', '=', active_id)])
        contract.compute_gs_date_end()

