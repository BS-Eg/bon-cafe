# -*- coding: utf-8 -*-

from odoo import api, fields, models ,_
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, time


class GsHrLeaveInherit(models.Model):
    _inherit = 'hr.leave'

    employee_ids = fields.Many2many('hr.employee', 'gs_lev_employee_ids_01', 'gs_lev_employee_ids_001', 'gs_lev_employee_ids_0001', string='Alternative Employee')

    @api.onchange('employee_id')
    def gs_domain_employee_id(self):
        for rec in self:
            return {'domain': {'employee_ids': [('id', 'in', rec.employee_id.gs_employee_ids.ids)]}}

    def make_activity_alternative_user(self, user):
        date_deadline = fields.Date.today()
        note = _("Please Review This Time Off")
        summary = _("Please Review This Time Off")

        self.sudo().activity_schedule(
            'mail.mail_activity_data_todo', date_deadline,
            note=note,
            user_id=user.id,
            res_id=self.id,
            summary=summary
        )

    def make_activity_employee_user(self, user):
        date_deadline = fields.Date.today()
        note = _("Your Time Off Approved")
        summary = _("Your Time Off Approved")

        self.sudo().activity_schedule(
            'mail.mail_activity_data_todo', date_deadline,
            note=note,
            user_id=user.id,
            res_id=self.id,
            summary=summary
        )

    def action_approve(self):
        self.make_activity_employee_user(self.employee_id.user_id)
        for uesr in self.user_ids:
            self.make_activity_alternative_user(uesr)

        print("done")
        res = super(GsHrLeaveInherit, self).action_approve()
        return res
