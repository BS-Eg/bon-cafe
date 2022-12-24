# -*- coding: utf-8 -*-

from odoo import models, fields, api


class GsAlarm(models.Model):
    _name = 'gs.alarm'
    _description = 'Alarm'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _interval_selection = {'minutes': 'Minutes', 'hours': 'Hours', 'days': 'Days'}

    name = fields.Char('Name', translate=True,)
    alarm_type = fields.Selection(
        [('notification', 'Notification'), ('email', 'Email')],
        string='Type', required=True, default='email')

    duration = fields.Integer('Remind Before', required=True, default=1)
    interval = fields.Selection(
        list(_interval_selection.items()), 'Unit', required=True, default='hours')

    @api.onchange('duration', 'interval', 'alarm_type')
    def _onchange_duration_interval(self):
        display_interval = self._interval_selection.get(self.interval, '')
        display_alarm_type = {
            key: value for key, value in self._fields['alarm_type']._description_selection(self.env)
        }[self.alarm_type]
        self.name = "%s - %s %s" % (display_alarm_type, self.duration, display_interval)