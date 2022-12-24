# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
import pytz
from pytz import timezone, UTC


class GsNotification(models.Model):
    _name = 'gs.notification'
    _description = 'Notification'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'type_of_notification'

    def get_type_of_notification(self):
        for rec in self:
            type_of_notification = {
                'ident_id': 'Identification ID',
                'driving_license': 'Driving License',
                'passport_id': 'Passport ID',
                'medical_card': 'Medical Card',
                'employee_contract': 'Employee Contract',
                'contract_management': 'Contract Management',
            }
            return type_of_notification[rec.type_of_notification]

    employee_id = fields.Many2one('hr.employee')
    type_of_notification = fields.Selection(string='Type Of Notification', selection=[
        ('ident_id', 'Identification ID'),
        ('driving_license', 'Driving License'),
        ('passport_id', 'Passport ID'),
        ('medical_card', 'Medical Card'),
        ('employee_contract', 'Employee Contract'),
        ('contract_management', 'Contract Management'),
    ], required=False, )
    date = fields.Datetime(tring='Date', )
    days_to_renew = fields.Integer(string='Days To Renew', )
    state = fields.Selection([
        ('new', 'New'),
        ('processing', 'Processing'),
        ('done', 'Done'),
        ('canceled', 'Canceled')
    ], string='Status', tracking=True, copy=False, default='new', )

    notify_ids = fields.Many2many('gs.alarm', string="Notify")
    partner_id = fields.Many2one('res.partner', string='Partner')
    recipient_users = fields.Text()
    filed_type_of_notification = fields.Text()
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    active = fields.Boolean(default=True, tracking=True, store=True)

    @api.onchange('type_of_notification')
    def onchange_method(self):
        for rec in self:
            if rec.type_of_notification:
                notification_type = self.env['gs.notification.user'].search([('type_of_notification', '=', rec.type_of_notification)])
                rec.notify_ids = notification_type.notify_ids

    def action_processing(self):
        self.write({'state': 'processing'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'canceled'})

    def _cron_get_data(self):
        employees = self.env['hr.employee'].search([('is_get_data_notification', '=', False)])
        contract_management = self.env['gs.contract.management'].search([('is_get_data_notification', '=', False)])
        vals = []
        for con in contract_management:
            notification_type = self.env['gs.notification.user'].search(
                [('type_of_notification', '=', 'contract_management')])
            today = date.today()
            if con.is_renew and con.date_renew:
                if con.date_renew > today:
                    wd_diff = fields.Date.from_string(con.date_renew) - fields.Date.from_string(today)
                    contract_management_available_days = wd_diff.days
                    vals.append({
                        'partner_id': con.partner_id.id,
                        'type_of_notification': 'contract_management',
                        'date': con.date_renew,
                        'days_to_renew': contract_management_available_days,
                        'notify_ids': notification_type.notify_ids,
                        'state': 'new',
                    })
            con.is_get_data_notification = True
        for employee in employees:
            today = date.today()
            contract = self.env['hr.contract'].search([('state', '=', 'open'), ('employee_id', '=', employee.id),
                                                       ('is_get_data_notification', '=', False)], limit=1)

            if employee.id_expiry_date and employee.is_get_id_expiry_date == False:
                notification_type_id_expiry = self.env['gs.notification.user'].search(
                    [('type_of_notification', '=', 'ident_id')])
                if employee.id_expiry_date > today:
                    wd_diff = fields.Date.from_string(employee.id_expiry_date) - fields.Date.from_string(today)
                    ident_id_available_days = wd_diff.days
                    vals.append({
                        'employee_id': employee.id,
                        'type_of_notification': 'ident_id',
                        'date': employee.id_expiry_date,
                        'days_to_renew': ident_id_available_days,
                        'notify_ids': notification_type_id_expiry.notify_ids,
                        'state': 'new',
                    })
                employee.is_get_id_expiry_date = True
            if employee.expiry_driving_license_date and employee.is_get_expiry_driving_license == False:
                notification_type_driving_license = self.env['gs.notification.user'].search(
                    [('type_of_notification', '=', 'driving_license')])
                if employee.expiry_driving_license_date > today:
                    wd_diff = fields.Date.from_string(employee.expiry_driving_license_date) - fields.Date.from_string(
                        today)
                    driving_license_available_days = wd_diff.days
                    vals.append({
                        'employee_id': employee.id,
                        'type_of_notification': 'driving_license',
                        'date': employee.expiry_driving_license_date,
                        'days_to_renew': driving_license_available_days,
                        'notify_ids': notification_type_driving_license.notify_ids,
                        'state': 'new',
                    })
                employee.is_get_expiry_driving_license = True
            if employee.passport_expiry_date and employee.is_get_passport_expiry == False:
                notification_type_passport_id = self.env['gs.notification.user'].search(
                    [('type_of_notification', '=', 'passport_id')])
                if employee.passport_expiry_date > today:
                    wd_diff = fields.Date.from_string(employee.passport_expiry_date) - fields.Date.from_string(today)
                    passport_id_available_days = wd_diff.days
                    vals.append({
                        'employee_id': employee.id,
                        'type_of_notification': 'passport_id',
                        'date': employee.passport_expiry_date,
                        'days_to_renew': passport_id_available_days,
                        'notify_ids': notification_type_passport_id.notify_ids,
                        'state': 'new',
                    })
                employee.is_get_passport_expiry = True
            if employee.expiry_medical_card_date and employee.is_get_expiry_medical_card == False:
                notification_type_medical_card = self.env['gs.notification.user'].search(
                    [('type_of_notification', '=', 'passport_id')])
                if employee.expiry_medical_card_date > today:
                    wd_diff = fields.Date.from_string(employee.expiry_medical_card_date) - fields.Date.from_string(
                        today)
                    medical_card_available_days = wd_diff.days
                    vals.append({
                        'employee_id': employee.id,
                        'type_of_notification': 'medical_card',
                        'date': employee.expiry_medical_card_date,
                        'days_to_renew': medical_card_available_days,
                        'notify_ids': notification_type_medical_card.notify_ids,
                        'state': 'new',
                    })
                employee.is_get_expiry_medical_card = True

            if contract.date_end:
                notification_type_employee_contract = self.env['gs.notification.user'].search(
                    [('type_of_notification', '=', 'employee_contract')])
                if contract.date_end > today:
                    wd_diff = fields.Date.from_string(contract.date_end) - fields.Date.from_string(today)
                    employee_contract_available_days = wd_diff.days
                    vals.append({
                        'employee_id': employee.id,
                        'type_of_notification': 'employee_contract',
                        'date': contract.date_end,
                        'days_to_renew': employee_contract_available_days,
                        'notify_ids': notification_type_employee_contract.notify_ids,
                        'state': 'new',
                    })
            contract.is_get_data_notification = True
            employee.is_get_data_notification = True
        self.env["gs.notification"].create(vals)

    def send_template_email(self, users):
        recipient_users = []
        for recipient in users:
            if recipient.employee_id.work_email not in recipient_users:
                recipient_users.append(recipient.employee_id.work_email)

        recipient_users = '[%s]' % ', '.join(map(str, recipient_users))
        self.recipient_users = recipient_users

        template_id = self.env.ref('gs_notification.gs_send_email_notification_template').id
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)

    def make_activity_user(self, user):
        date_deadline = fields.Date.today()
        note = _("Please Review This Request")
        summary = _("Notification")

        self.sudo().activity_schedule(
            'mail.mail_activity_data_todo', date_deadline,
            note=note,
            user_id=user.id,
            res_id=self.id,
            summary=summary
        )

    notifi_minutes = fields.Datetime(store=True)
    notifi_hours = fields.Datetime(store=True)
    notifi_day = fields.Date(store=True)

    email_minutes = fields.Datetime(store=True)
    email_hours = fields.Datetime(store=True)
    email_day = fields.Date(store=True)

    def _cron_send_notification_in_minutes(self):
        notifications = self.env['gs.notification'].search([])
        date_now = fields.Datetime.now()
        for notif in notifications:
            notification_users = self.env['gs.notification.user'].search(
                [('type_of_notification', '=', notif.type_of_notification)])
            if notification_users:
                if notif.notifi_minutes:
                    users = notification_users.user_ids
                    for user in users:
                        if date_now.minute == notif.notifi_minutes.minute:
                            notif.make_activity_user(user)

    def _cron_send_notification_in_hours(self):
        notifications = self.env['gs.notification'].search([])
        date_now = fields.Datetime.now()
        for notif in notifications:
            notification_users = self.env['gs.notification.user'].search(
                [('type_of_notification', '=', notif.type_of_notification)])
            if notification_users:
                if notif.notifi_hours:
                    users = notification_users.user_ids
                    for user in users:
                        if date_now.hour == notif.notifi_hours.hour:
                            notif.make_activity_user(user)

    def _cron_send_notification_in_day(self):
        notifications = self.env['gs.notification'].search([])
        date = fields.Date.today()
        for notif in notifications:
            notification_users = self.env['gs.notification.user'].search(
                [('type_of_notification', '=', notif.type_of_notification)])
            if notification_users:
                if notif.notifi_day:
                    users = notification_users.user_ids
                    for user in users:
                        if date == notif.notifi_day:
                            notif.make_activity_user(user)

    def _cron_send_email_in_minutes(self):
        notifications = self.env['gs.notification'].search([])
        date_now = fields.Datetime.now()
        for notif in notifications:
            notification_users = self.env['gs.notification.user'].search(
                [('type_of_notification', '=', notif.type_of_notification)])
            if notification_users:
                if notif.notifi_minutes:
                    users = notification_users.user_ids
                    for user in users:
                        if date_now.minute == notif.notifi_minutes.minute:
                            notif.send_template_email(user)

    def _cron_send_email_in_hours(self):
        notifications = self.env['gs.notification'].search([])
        date_now = fields.Datetime.now()
        for notif in notifications:
            notification_users = self.env['gs.notification.user'].search(
                [('type_of_notification', '=', notif.type_of_notification)])
            if notification_users:
                if notif.notifi_hours:
                    users = notification_users.user_ids
                    for user in users:
                        if date_now.hour == notif.notifi_hours.hour:
                            notif.send_template_email(user)

    def _cron_send_email_in_day(self):
        notifications = self.env['gs.notification'].search([])
        date = fields.Date.today()
        for notif in notifications:
            notification_users = self.env['gs.notification.user'].search(
                [('type_of_notification', '=', notif.type_of_notification)])
            if notification_users:
                if notif.notifi_day:
                    users = notification_users.user_ids
                    for user in users:
                        if date == notif.notifi_day:
                            notif.send_template_email(user)

    def _cron_send_notification(self):
        notifications = self.env['gs.notification'].search([])
        for notif in notifications:
            date_now = notif.date
            for notify in notif.notify_ids:
                if notify.alarm_type == 'email':
                    if notify.interval == 'minutes':
                        notif.email_minutes = date_now - timedelta(minutes=notify.duration)

                    if notify.interval == 'hours':
                        notif.email_hours = date_now - timedelta(hours=notify.duration)

                    if notify.interval == 'days':
                        notif.email_day = date_now - timedelta(days=notify.duration)

                elif notify.alarm_type == 'notification':
                    if notify.interval == 'minutes':
                        notif.notifi_minutes = date_now - timedelta(minutes=notify.duration)

                    if notify.interval == 'hours':
                        notif.notifi_hours = date_now - timedelta(hours=notify.duration)

                    if notify.interval == 'days':
                        notif.notifi_day = date_now - timedelta(days=notify.duration)
