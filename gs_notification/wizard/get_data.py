# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class GsGetDataWizard(models.TransientModel):
    _name = "get.data.wizard"

    def action_get_data(self):
        active_id = self.env.context.get('active_id')
        notification = self.env['gs.notification'].search([('id', '=', active_id)])
        notification._cron_get_data()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }