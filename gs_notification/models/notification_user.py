# -*- coding: utf-8 -*-

from odoo import models, fields, api


class GsNotificationUsers(models.Model):
    _name = 'gs.notification.user'
    _description = 'Notification'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'type_of_notification'

    type_of_notification = fields.Selection(string='Type Of Notification', selection=[
        ('ident_id', 'Identification ID'),
        ('driving_license', 'Driving License'),
        ('passport_id', 'Passport ID'),
        ('medical_card', 'Medical Card'),
        ('employee_contract', 'Employee Contract'),
        ('contract_management', 'Contract Management'),
    ], required=False, )

    user_ids = fields.Many2many('res.users', 'gs_user01', 'gs_user001', 'gs_user0001', 'Users')
    notify_ids = fields.Many2many('gs.alarm', string="Notify")

    _sql_constraints = [
        ('type_of_notification_uniq', 'unique (type_of_notification)',
         """Type Of Notification already exists!"""),
    ]
